import json
from datetime import datetime


import requests

from ADMINKA.config.config import API_KEY


# Ваш API-ключ


def get_today_date():
    return datetime.now().strftime("%d.%m.%Y")



# Параметры запроса
params = {
    "begin_date": "1.11.2024",  # Начало периода
    "end_date": get_today_date(),  # Конец периода
    "user_ids[]": [12327,12477,12330,12532,12511,12408,12331,12616,12614,12333,12615,12561,12610,12594,12357,12595,12575,12461,12462,12463]
}


# Заголовки запроса
headers = {
    "X-API-KEY": API_KEY
}

# URL для получения звонков
BASE_URL = "https://app.obzvonilka.ru"
call_history_url = f"{BASE_URL}/api/report/call_history"

# Определение статусов горячих лидов, перезвона и отложенного спроса
hot_leads_statuses = [
    "Горячий лид",
    "Горячий лид (Входная дверь)"
]

call_back_statuses = [
    "Перезвонить (Есть интерес)"
]

delayed_demand_statuses = [
    "Отложенный спрос (Есть интерес) "
]

# Отправка запроса для получения списка звонков
response = requests.get(call_history_url, params=params, headers=headers)

# Проверка успешности запроса
if response.status_code == 200:
    json_data = response.json()

    # Переменная для хранения результатов
    result_data = {}

    # Проход по каждому звонку
    for x in json_data:
        project_name = x.get('project_name', 'Неизвестный проект')[:100]
        contact_name = x.get('contact_name', 'Неизвестный источник')
        call_result_name = x.get('call_result_name', 'Неизвестный статус')
        created_at = x.get('created_at', 'Неизвестная дата')

        # Преобразуем дату в формат %Y-%m-%d
        try:
            date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%Y-%m-%d')
        except ValueError:
            date = 'Неизвестная дата'

        # Проверяем и фильтруем по статусам
        if any(status in call_result_name for status in hot_leads_statuses):
            lead_status = "горячие_лиды"
        elif any(status in call_result_name for status in call_back_statuses):
            lead_status = "перезвонить"
        elif any(status in call_result_name for status in delayed_demand_statuses):
            lead_status = "отложенный_спрос"
        else:
            lead_status = None

        if lead_status:
            if date not in result_data:
                result_data[date] = {}

            if project_name not in result_data[date]:
                result_data[date][project_name] = {}

            if contact_name not in result_data[date][project_name]:
                result_data[date][project_name][contact_name] = {"горячие_лиды": 0, "перезвонить": 0,
                                                                 "отложенный_спрос": 0, "звонки": 0}

            # Увеличиваем счетчик по соответствующему статусу
            result_data[date][project_name][contact_name][lead_status] += 1
        else:
            if date not in result_data:
                result_data[date] = {}

            if project_name not in result_data[date]:
                result_data[date][project_name] = {}

            if contact_name not in result_data[date][project_name]:
                result_data[date][project_name][contact_name] = {"горячие_лиды": 0, "перезвонить": 0,
                                                                 "отложенный_спрос": 0, "звонки": 0}

        # Увеличиваем общий счетчик звонков
        result_data[date][project_name][contact_name]["звонки"] += 1

    # Сохранение результатов в JSON файл
    with open('static/compact_contact_sources.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)

    print('Завершено')

else:
    print(f"Ошибка при запросе данных: {response.status_code}")
