import requests

url = "http://localhost:5000/register"
headers = {"Content-Type": "application/json"}
data = {
    "first_name": "Иван",
    "last_name": "Иванов",
    "patronymic": "Иванович",
    "email": "ivanov@example.com",
    "password": "password123"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
