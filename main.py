from flask import Flask, request, jsonify, send_from_directory
import os
import re
import bcrypt
import psycopg2
from flask_cors import CORS
from flask_pymongo import PyMongo
from bson import ObjectId, json_util
from dotenv import load_dotenv
import json

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)  
CORS(app)

# Настройка подключения к MongoDB
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise RuntimeError("Переменная окружения MONGO_URI не задана")
app.config["MONGO_URI"] = mongo_uri

try:
    mongo = PyMongo(app)
    db = mongo.db
    db.list_collection_names()  # Проверка подключения
    print("Успешное подключение к MongoDB")
except Exception as e:
    print(f"Ошибка подключения к MongoDB: {e}")
    raise RuntimeError("Проблема с доступом к базе данных MongoDB")

# Роут для сохранения данных телеметрии (MongoDB)
@app.route('/submit-data', methods=['POST'])
def submit_data():
    try:
        # Логируем заголовки запроса
        app.logger.info(f"Заголовки: {request.headers}")

        # Проверяем Content-Type
        if request.content_type != 'application/json':
            app.logger.error("Некорректный Content-Type")
            return jsonify({"error": "Content-Type должен быть application/json"}), 415

        # Логируем сырые данные запроса
        app.logger.info(f"Сырые данные: {request.data.decode('utf-8')}")

        # Получаем JSON-данные из запроса
        data = request.get_json(silent=True)
        if not data:
            app.logger.error("Неверный формат JSON или пустое тело запроса")
            return jsonify({"error": "Неверный формат JSON или пустое тело запроса"}), 400

        # Определяем, какая форма была отправлена, на основе обязательных полей
        form_type = None
        
        # Обязательные поля для первой формы (форма телеметрии автомобиля)
        vehicle_form_fields = ['car_id', 'probeg_km', 'battery_age_months']
        missing_vehicle_fields = [field for field in vehicle_form_fields if field not in data or not data[field]]
        
        # Обязательные поля для второй формы (форма расчёта маршрута)
        route_form_fields = ['start_point', 'end_point', 'current_charge']
        missing_route_fields = [field for field in route_form_fields if field not in data or not data[field]]
        
        # Определяем, какая форма была отправлена
        if not missing_vehicle_fields:
            form_type = "vehicle_form"
        elif not missing_route_fields:
            form_type = "route_form"
        
        if form_type == "vehicle_form":
            # Логируем валидные данные для формы телеметрии автомобиля
            app.logger.info(f"Данные формы автомобиля получены: {data}")
        
            # Сохраняем данные в MongoDB
            result = db.telemetry.insert_one({**data, "form_type": "vehicle_form"})
            app.logger.info(f"Данные формы автомобиля успешно сохранены с ID: {result.inserted_id}")
        
            response = {
                "message": "Данные формы автомобиля успешно сохранены",
                "id": str(result.inserted_id),
                "data": data
            }
            
        elif form_type == "route_form":
            # Логируем валидные данные для формы расчёта маршрута
            app.logger.info(f"Данные формы маршрута получены: {data}")
        
            # Сохраняем данные в MongoDB
            result = db.telemetry.insert_one({**data, "form_type": "route_form"})
            app.logger.info(f"Данные формы маршрута успешно сохранены с ID: {result.inserted_id}")
        
            response = {
                "message": "Данные формы маршрута успешно сохранены",
                "id": str(result.inserted_id),
                "data": data
            }
        
        else:
            # Если ни одна из форм не совпадает с обязательными полями, возвращаем сообщение об ошибке
            app.logger.error("Отсутствуют обязательные поля для обеих форм")
            return jsonify({"error": "Отсутствуют обязательные поля для формы автомобиля или формы маршрута"}), 400

        # Возвращаем корректно сериализованный JSON-ответ
        return app.response_class(
            response=json_util.dumps(response),
            status=201,
            mimetype='application/json'
        )
    
    except Exception as e:
        app.logger.error(f"Ошибка сервера: {e}")
        return jsonify({"error": "Ошибка сервера"}), 500


# Роут для статических файлов
@app.route('/<path:filename>')
def serve_static_files(filename):
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site')
    return send_from_directory(directory, filename)

# Главная страница
@app.route('/')
def serve_index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.join(base_dir, 'site')
    index_file = os.path.join(directory, 'index.html')

    app.logger.info(f"Главная страница: {index_file}")
    if not os.path.exists(index_file):
        app.logger.error("Файл index.html не найден")
        return jsonify({'error': 'Файл index.html не найден'}), 404

    return send_from_directory(directory, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
