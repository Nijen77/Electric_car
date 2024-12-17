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

# Настройка подключения к PostgreSQL
def get_db_connection():
    try:
        return psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT')
        )
    except psycopg2.OperationalError as e:
        app.logger.error(f"Ошибка подключения к PostgreSQL: {str(e)}")
        raise

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

# Роут для регистрации пользователя (PostgreSQL)
@app.route('/register', methods=['POST'])
def register_user():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Content-Type должен быть application/json'}), 415

    try:
        app.logger.info("\n=== Поступил запрос ===")
        app.logger.info(f"Заголовки запроса: {request.headers}")
        app.logger.info(f"Тело запроса (сырое): {request.data}")

        try:
            data = request.get_json()
        except Exception as e:
            app.logger.error(f"Ошибка получения JSON из запроса: {e}")
            return jsonify({'error': 'Неверный формат JSON'}), 400

        if not data:
            app.logger.error("Пустое тело запроса")
            return jsonify({'error': 'Тело запроса пустое'}), 400

        app.logger.info(f"Тело запроса (JSON): {data}")
    except Exception as e:
        app.logger.error(f"Ошибка сервера: {str(e)}")
        return jsonify({'error': 'Ошибка сервера'}), 500

    try:
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        patronymic = data.get('patronymic')
        email = data.get('email')
        password = data.get('password')

        if not first_name or not last_name or not email or not password:
            return jsonify({'error': 'Обязательные поля не заполнены'}), 400

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Неверный формат email'}), 400

        if len(password) < 8:
            return jsonify({'error': 'Пароль должен быть не менее 8 символов'}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')

        query_check_email = "SELECT COUNT(*) FROM el_car_users WHERE email = %s"
        query_insert_user = """
            INSERT INTO el_car_users (first_name, last_name, patronymic, email, passwordhash)
            VALUES (%s, %s, %s, %s, %s)
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query_check_email, (email,))
                if cur.fetchone()[0] > 0:
                    return jsonify({'error': 'Этот email уже зарегистрирован'}), 409

                cur.execute(query_insert_user, (first_name, last_name, patronymic, email, hashed_password))
                conn.commit()

        return jsonify({'message': 'Пользователь успешно зарегистрирован'}), 201

    except psycopg2.OperationalError:
        return jsonify({'error': 'Не удалось подключиться к PostgreSQL'}), 500
    except Exception as e:
        app.logger.error(f'Ошибка сервера: {str(e)}')
        return jsonify({'error': 'Ошибка сервера'}), 500

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
        vehicle_form_fields = ['car_model', 'mileage', 'usage_time', 'usage_frequency']
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
    
# Роут для просмотра сохраненных данных (MongoDB)
@app.route('/view-data', methods=['GET'])
def view_data():
    try:
        data = list(db.telemetry.find({}, {'_id': 0}))  # Убираем ObjectId для удобства
        return jsonify({'data': data}), 200
    except Exception as e:
        app.logger.error(f'Ошибка сервера: {str(e)}')
        return jsonify({'error': 'Ошибка сервера'}), 500

# Роут для получения данных
@app.route('/users')
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, first_name, last_name, email FROM el_car_users;')
        users = cursor.fetchall()  # Получаем все данные
        cursor.close()
        conn.close()

        # Форматируем результат для JSON-ответа
        users_list = [
            {'id': user[0], 'first_name': user[1], 'last_name': user[2], 'email': user[3]} 
            for user in users
        ]
        return jsonify(users_list)  # Возвращаем данные в формате JSON

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
