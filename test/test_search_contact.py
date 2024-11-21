import requests

# Ваш API-ключ
api_key = "CrWtR636gPGkQvh4dE6Pq3fjxXWyJXaw"
# Базовый URL для получения звонков
BASE_URL = "app.obzvonilka.ru"
url = f'https://{BASE_URL}/api/report/contacts'
# Параметры запроса
payload = {
    "phone": "79500047795"
}
# Заголовки запроса
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
# Отправка запроса
response = requests.get(url, params=payload, headers=headers)

# Проверка ответа
if response.status_code == 200:
    print(response.text)
else:
    print(f"Ошибка {response.status_code}: {response.text}")
