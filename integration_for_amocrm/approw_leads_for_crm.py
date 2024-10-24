import logging
import os

import requests

# Создание директории для логов, если она не существует
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка логирования
logging.basicConfig(filename=os.path.join(log_dir, 'approv_process.log'), level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

token_bt_crm = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjRmODcwMTNlNTY0NmEzMDgyMjNlM2EzMzkyNjM3Zjk4NDNlNDQyNDNmMmFiYzI0NDcwMGQyZWI4ZWU2MTUzZmZmZDZiNzdiZTUyMzYyMzI1In0.eyJhdWQiOiJiNTU1ZGU5MS04Yjc3LTQ4ZWUtYjRkZC01MmM5NGFhMTJlY2YiLCJqdGkiOiI0Zjg3MDEzZTU2NDZhMzA4MjIzZTNhMzM5MjYzN2Y5ODQzZTQ0MjQzZjJhYmMyNDQ3MDBkMmViOGVlNjE1M2ZmZmQ2Yjc3YmU1MjM2MjMyNSIsImlhdCI6MTcyODExMDg3MCwibmJmIjoxNzI4MTEwODcwLCJleHAiOjE3NjcxMzkyMDAsInN1YiI6IjExMTM0NDk4IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNzgwNDE0LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiNDE5MjUwYTAtMDVlOS00NWY1LWJhNGUtZWYwYjA4NDdjOTI4IiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.BELBcwM5fJ_wAAoTB8ysbJ598sXrWId5cI-q-_HxBgUcM2hhQlUDIIheXQNkQu5S3aNNdtA5rtbmG3WVqJeBk4JYzmyC7SF4QyGXNbGVmKGheeprc9-FicxlhxvLaXMQ59AwZYNyoNT7NheZykqppXTNO5aWbwQ5Osoy7v6r1uRZb8Dg8zMyJG2qSUqyhFXnQS1dtnDeBYOvQ9ojuluFWnh1DbCfpeuGSQhTKF-SqE2rma6MwfPWGAJjhpia3CI3iWsV3C3247ySYCESv6yBNdVB1HuPBFR9J3FqlcG52jXckCS5Eg42VTTb8gBO8brEc-Coap8QPM_KHSxSZDgXYg'

headers = {
    'Authorization': f'Bearer {token_bt_crm}',
    'Content-Type': 'application/json'
}

pipline_id = 8701282

responsible_user_id = 11134498  # Евгений
created_by = responsible_user_id  # Используем того же пользователя, который будет ответственным
position_field_id = 298435  # ID поля "Должность"
phone_field_id = 298437  # ID поля "Телефон"
email_field_id = 298439  # ID поля "Email"


# Функция для обработки строки данных и отправки запроса
def process_row(name, city, phone, project_id, manager_name, audio, note):
    complex_data = [
        {
            "name": f'{name}',
            "price": 0,
            "pipeline_id": pipline_id,
            "status_id": 70487722,
            "responsible_user_id": responsible_user_id,
            "custom_fields_values": [
                {
                    "field_id": 781061,
                    "values": [{"value": audio}]  # ссылка на аудио
                },
                {
                    "field_id": 778649,
                    "values": [{"value": manager_name}]  # источник
                },
                {
                    "field_id": 778647,
                    "values": [{"value": project_id}]
                },
                {
                    "field_id": 781057,
                    "values": [{"value": phone}]
                },
                {
                    "field_id": 781059,
                    "values": [{"value": city}]
                },
            ],
            "_embedded": {
                "contacts": [
                    {
                        "first_name": name,
                        "responsible_user_id": responsible_user_id,
                        "created_by": created_by,
                        "custom_fields_values": [
                            {
                                "field_id": phone_field_id,
                                "values": [{"value": phone}]
                            }
                        ]
                    }
                ]
            }
        }
    ]

    response = requests.post("https://infoboardtraffru.amocrm.ru/api/v4/leads/complex", json=complex_data,
                             headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        if isinstance(response_json, list) and len(response_json) > 0:
            lead_id = response_json[0]['id']
            print(f"Сделка успешно создана. ID сделки: {lead_id}")

            note_data = [
                {
                    "entity_id": lead_id,
                    "note_type": "common",
                    "params": {
                        "text": f"{note}"
                    }
                }
            ]

            note_response = requests.post(f"https://infoboardtraffru.amocrm.ru/api/v4/leads/{lead_id}/notes",
                                          json=note_data,
                                          headers=headers)

            if note_response.status_code == 200:
                print(f"Примечание успешно добавлено к сделке {lead_id}")
            else:
                print(f"Ошибка при добавлении примечания к сделке {lead_id}: {note_response.status_code}")
        else:
            print("Не удалось получить ID созданной сделки")
    else:
        print("Ошибка при создании сделки:", response.status_code)

# process_row('Имя клиента', '+79999999999', 'МК ГРУПП  (Санкт Петербург)','Имя оператора','https://app.obzvonilka.ru/v/fd122396-65e9-43db-8893-9c5067454ea9.mp3','Интересуется покупкой межкомнатных дверей, которые не разбухают и могут быть окрашены. Клиент планирует купить 7 или 8 таких дверей и ожидает звонка от менеджера для получения более подробной информации о стоимости. Клиент также хочет узнать, как обращаться к соответствующим уголкам. Ожидает звонка в ближайшие дни.' )
