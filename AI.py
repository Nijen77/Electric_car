import os
import numpy as np
from pymongo import MongoClient
from dotenv import load_dotenv
import joblib
import pandas as pd
from bson import ObjectId
from flask import Flask, request, jsonify
load_dotenv()
MONGO_URI = os.getenv("mongodb+srv://rybasevgenij:Y2UNBkpw7b4CWAl9@elcartest.rygnv.mongodb.net/cartelem")

app = Flask(__name__)

# === Основной процесс ===
if __name__ == "__main__":
    # Параметры подключения к MongoDB
    mongodb_uri = "mongodb+srv://rybasevgenij:Y2UNBkpw7b4CWAl9@elcartest.rygnv.mongodb.net/cartelem"
    db_name = "ev_database"
    collection_name = "ev_specs"

# Подключение к MongoDB
def connect_to_mongodb(uri, db_name, collection_name):
    """
    Подключение к MongoDB
    :param uri: Строка подключения к MongoDB
    :param db_name: Имя базы данных
    :param collection_name: Имя коллекции
    :return: Коллекция MongoDB
    """
    client = MongoClient(uri)
    db = client[db_name]
    collection = db[collection_name]
    return collection

@app.route('/predict', methods=['POST'])
def run_prediction():
    try:
        data = request.json
        car_id = data.get("car_id")  # Извлекаем car_id из запроса
        if not car_id:
            return jsonify({"error": "car_id не указан"}), 400
        probeg_km = data.get("probeg_km")
        battery_age_months = data.get("battery_age_months")
        if not probeg_km or not battery_age_months:
            return jsonify({"error": "Параметры probeg_km и battery_age_months обязательны"}), 400

        # Подключение к MongoDB
        collection = connect_to_mongodb(mongodb_uri, db_name, collection_name)
        
        # Получение данных о машине
        car_data = get_car_data(collection, car_id)

        if not car_data:
            return jsonify({"error": f"Машина с ID {car_id} не найдена."}), 400

        # Извлекаем параметры
        battery_capacity_kwh = car_data.get("battery_capacity_kwh")
        avg_consumption_kwh_per_km = car_data.get("avg_consumption_kwh_per_km")
        temperature = car_data.get("temperature")
        
        charge_cycles, adjusted_dod = calculate_dod_and_cycles(
            probeg_km, battery_age_months, battery_capacity_kwh, avg_consumption_kwh_per_km
        )
        print(f"Вычислено количество циклов зарядки: {charge_cycles}")
        print(f"Вычислено средняя глубина разряда (DoD): {adjusted_dod}")

        # Сохранение DoD и циклов в MongoDB
        collection.update_one(
            {"_id": ObjectId(car_id)},
            {"$set": {"adjusted_dod": adjusted_dod, "charge_cycles": charge_cycles}}
        )
        print("Результаты расчёта DoD и циклов сохранены в MongoDB.")

        # Предсказание износа
        degradation = predict_degradation(probeg_km, charge_cycles, adjusted_dod, temperature, battery_age_months)
        print(f"Предсказанный износ для ID {car_id}: {degradation}%")

        # Генерация рекомендаций
        recommendations = generate_recommendations(degradation)
        print(f"Рекомендации: {recommendations}")

        # Сохранение предсказания и рекомендаций в MongoDB
        collection.update_one(
            {"_id": ObjectId(car_id)},
            {"$set": {"predicted_degradation": degradation, "recommendations": recommendations}}
        )
        print("Предсказание износа и рекомендации сохранены в MongoDB.")

        # Возвращаем результат клиенту
        return jsonify({
            "car_id": car_id,
            "degradation": degradation,
            "recommendations": recommendations
        }), 200

    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": str(e)}), 500


# Подключение к MongoDB
collection = connect_to_mongodb(mongodb_uri, db_name, collection_name)

def calculate_dod_and_cycles(probeg_km, battery_age_months, battery_capacity_kwh, avg_consumption_kwh_per_km, avg_dod=0.7):
    """
    Расчет количества циклов зарядки и средней глубины разряда (DoD)
    :param probeg_km: Пробег автомобиля (км)
    :param battery_age_months: Возраст батареи (месяцы)
    :param battery_capacity_kwh: Емкость батареи (кВт·ч)
    :param avg_consumption_kwh_per_km: Средний расход энергии (кВт·ч на км)
    :param avg_dod: Средняя глубина разряда (по умолчанию 70%)
    :return: Количество циклов зарядки, Средняя глубина разряда (DoD)
    """
    
    # Оценка количества циклов зарядки
    total_energy_used_kwh = probeg_km * (avg_consumption_kwh_per_km / 100)  # Общее потребление энергии за весь пробег
    charge_cycles = total_energy_used_kwh / (battery_capacity_kwh * avg_dod)  # Количество полных циклов
    
    # Коррекция DoD на основе возраста батареи (допущение: со временем DoD уменьшается)
    # Уменьшаем DoD на 0.01 (1%) за каждый год, что эквивалентно 0.000833 (0.0833%) за каждый месяц
    adjusted_dod = max(0.5, min(0.9, avg_dod - (battery_age_months * 0.000833)))  # DoD уменьшается на 0.0833% в месяц
    return round(charge_cycles, 2), round(adjusted_dod, 2)

# Получение данных о машине по её ID
def get_car_data(collection, car_id):
    """
    Получение данных о машине по её ID
    :param collection: Коллекция MongoDB
    :param car_id: ID машины (строка или ObjectId)
    :return: Данные о машине
    """
    # Преобразуем car_id в ObjectId, если это необходимо
    try:
        car_id = ObjectId(car_id)  # Пробуем преобразовать строку в ObjectId
    except:
        pass  # Если преобразование не удалось, оставляем car_id как строку

    car_data = collection.find_one({"_id": car_id})  # Ищем по _id
    if not car_data:
        raise ValueError(f"Машина с ID {car_id} не найдена.")
    return car_data

# Сохранение результатов в MongoDB
def save_calculation_results(collection, car_id, charge_cycles, adjusted_dod):
    """
    Сохранение результатов расчёта в документ автомобиля
    :param collection: Коллекция MongoDB
    :param car_id: ID машины (строка)
    :param charge_cycles: Количество циклов зарядки
    :param adjusted_dod: Средняя глубина разряда (DoD)
    """
    collection.update_one(
        {"_id": ObjectId(car_id)},  # Используем "id" как строку
        {"$set": {"charge_cycles": charge_cycles, "adjusted_dod": adjusted_dod}}
    )
    
# === Функция для предсказания износа ===
def predict_degradation(probeg, cycles, dod, temperature, age):
    model = joblib.load("battery_degradation_model.pkl")
    scaler = joblib.load("scaler.pkl")
    
    # Создаём DataFrame с именами признаков, которые использовались при обучении
    input_data = pd.DataFrame([[probeg, cycles, dod, temperature, age]],
    columns=["probeg", "cycles", "DoD", "temperature", "age"])
    
    # Масштабирование данных
    input_scaled = scaler.transform(input_data)
    
    # Предсказание
    prediction = model.predict(input_scaled)
    return round(prediction[0], 2)

# === Основной процесс ===
def generate_recommendations(degradation):
    """
    Генерация рекомендаций на основе износа батареи
    :param degradation: Износ батареи в процентах
    :return: Рекомендации
    """
    if degradation < 10:
        return (
            "Батарея в отличном состоянии (износ менее 10%).\n"
            "Продолжайте регулярное использование и следите за температурным режимом. "
            "Проводите плановое техническое обслуживание."
        )
    elif 10 <= degradation < 20:
        return (
            "Батарея в хорошем состоянии (износ 10-20%).\n"
            "Всё в норме, но рекомендуется проверить состояние батареи на следующем ТО. "
            "Избегайте экстремальных температур и глубоких разрядов."
        )
    elif 20 <= degradation < 40:
        return (
            "Батарея начинает терять ёмкость (износ 20-40%).\n"
            "Проведите диагностику батареи. Рассмотрите возможность замены в ближайшие 1-2 года. "
            "Избегайте частых быстрых зарядок и глубоких разрядов."
        )
    elif 40 <= degradation < 60:
        return (
            "Батарея значительно изношена (износ 40-60%).\n"
            "Рекомендуется заменить батарею в ближайшее время. "
            "Обратитесь в сервисный центр для диагностики и замены. "
            "Избегайте экстремальных условий эксплуатации."
        )
    elif 60 <= degradation < 80:
        return (
            "Батарея в критическом состоянии (износ 60-80%).\n"
            "Необходимо срочно заменить батарею. "
            "Обратитесь в сервисный центр для замены и полного технического обслуживания. "
            "Эксплуатация батареи в таком состоянии может быть опасной."
        )
    else:
        return (
            "Батарея в аварийном состоянии (износ более 80%).\n"
            "Немедленно прекратите использование батареи. "
            "Обратитесь в сервисный центр для замены батареи и полной диагностики автомобиля. "
            "Эксплуатация батареи в таком состоянии крайне опасна."
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)