 # token_bt_crm = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjRmODcwMTNlNTY0NmEzMDgyMjNlM2EzMzkyNjM3Zjk4NDNlNDQyNDNmMmFiYzI0NDcwMGQyZWI4ZWU2MTUzZmZmZDZiNzdiZTUyMzYyMzI1In0.eyJhdWQiOiJiNTU1ZGU5MS04Yjc3LTQ4ZWUtYjRkZC01MmM5NGFhMTJlY2YiLCJqdGkiOiI0Zjg3MDEzZTU2NDZhMzA4MjIzZTNhMzM5MjYzN2Y5ODQzZTQ0MjQzZjJhYmMyNDQ3MDBkMmViOGVlNjE1M2ZmZmQ2Yjc3YmU1MjM2MjMyNSIsImlhdCI6MTcyODExMDg3MCwibmJmIjoxNzI4MTEwODcwLCJleHAiOjE3NjcxMzkyMDAsInN1YiI6IjExMTM0NDk4IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNzgwNDE0LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiNDE5MjUwYTAtMDVlOS00NWY1LWJhNGUtZWYwYjA4NDdjOTI4IiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.BELBcwM5fJ_wAAoTB8ysbJ598sXrWId5cI-q-_HxBgUcM2hhQlUDIIheXQNkQu5S3aNNdtA5rtbmG3WVqJeBk4JYzmyC7SF4QyGXNbGVmKGheeprc9-FicxlhxvLaXMQ59AwZYNyoNT7NheZykqppXTNO5aWbwQ5Osoy7v6r1uRZb8Dg8zMyJG2qSUqyhFXnQS1dtnDeBYOvQ9ojuluFWnh1DbCfpeuGSQhTKF-SqE2rma6MwfPWGAJjhpia3CI3iWsV3C3247ySYCESv6yBNdVB1HuPBFR9J3FqlcG52jXckCS5Eg42VTTb8gBO8brEc-Coap8QPM_KHSxSZDgXYg'
import time
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Токен для отправки письма
token_bt_crm = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjRmODcwMTNlNTY0NmEzMDgyMjNlM2EzMzkyNjM3Zjk4NDNlNDQyNDNmMmFiYzI0NDcwMGQyZWI4ZWU2MTUzZmZmZDZiNzdiZTUyMzYyMzI1In0.eyJhdWQiOiJiNTU1ZGU5MS04Yjc3LTQ4ZWUtYjRkZC01MmM5NGFhMTJlY2YiLCJqdGkiOiI0Zjg3MDEzZTU2NDZhMzA4MjIzZTNhMzM5MjYzN2Y5ODQzZTQ0MjQzZjJhYmMyNDQ3MDBkMmViOGVlNjE1M2ZmZmQ2Yjc3YmU1MjM2MjMyNSIsImlhdCI6MTcyODExMDg3MCwibmJmIjoxNzI4MTEwODcwLCJleHAiOjE3NjcxMzkyMDAsInN1YiI6IjExMTM0NDk4IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNzgwNDE0LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiNDE5MjUwYTAtMDVlOS00NWY1LWJhNGUtZWYwYjA4NDdjOTI4IiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.BELBcwM5fJ_wAAoTB8ysbJ598sXrWId5cI-q-_HxBgUcM2hhQlUDIIheXQNkQu5S3aNNdtA5rtbmG3WVqJeBk4JYzmyC7SF4QyGXNbGVmKGheeprc9-FicxlhxvLaXMQ59AwZYNyoNT7NheZykqppXTNO5aWbwQ5Osoy7v6r1uRZb8Dg8zMyJG2qSUqyhFXnQS1dtnDeBYOvQ9ojuluFWnh1DbCfpeuGSQhTKF-SqE2rma6MwfPWGAJjhpia3CI3iWsV3C3247ySYCESv6yBNdVB1HuPBFR9J3FqlcG52jXckCS5Eg42VTTb8gBO8brEc-Coap8QPM_KHSxSZDgXYg'
headers = {
    'Authorization': f'Bearer {token_bt_crm}',
    'Content-Type': 'application/json'
}

url = 'https://amomail.amocrm.ru/api/v2/31780414/messages/send'

# Настроим доступ к Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('logical-air-353619-d959f6958ff1.json', scope)
client = gspread.authorize(creds)

# Получаем таблицу
spreadsheet = client.open_by_url(
    'https://docs.google.com/spreadsheets/d/1-gV-0zTNFVMpYrVeZHvsLsHBAbTX5hfJZClsOhizKoI/edit?gid=1129040397#gid=1129040397')
worksheet = spreadsheet.get_worksheet(0)

# Инициализируем переменную для хранения последнего числа строк
current_row_count = len(worksheet.get_all_values())

def process_row_window(row_number, row):
    name = row[1] if len(row) > 1 else ""
    phone = row[0] if len(row) > 0 else ""
    comment = row[2] if len(row) > 2 else ""

    # Проверка на заполненность полей имени, телефона и комментария
    if not (name and phone and comment):
        print(f"Пропущена строка {row_number} из-за отсутствия данных в одном из полей (имя, телефон или комментарий).")
        return False  # Пропустить строку, если одно из полей пустое

    message_text = f"{phone}<br>{name}<br>{comment}"

    # Формируем данные для отправки письма
    data_form = {
        "subject": f"Лид ВТ",
        "attachments": {},
        "content_type": "html",
        "content": f"<div>{message_text}</div>",
        "template_fields": {"profile.name": "Илья", "profile.phone": "null"},
        "from": {"mailbox_id": "151359", "name": "Илья"},
        "to": [{"email": "isrgznn@gmail.com", "name": ""}]
    }

    # Отправляем письмо
    response = requests.post(url, headers=headers, data=json.dumps(data_form))
    if response.status_code == 202:
        print(f"Письмо отправлено: {name}")
        return True  # Письмо успешно отправлено
    else:
        print(f"Ошибка отправки письма: {response.status_code}")
        print(response.text)
        return False

def monitor_new_rows():
    global current_row_count
    while True:
        # Получаем все строки таблицы
        rows = worksheet.get_all_values()
        new_row_count = len(rows)

        # Проверяем, добавились ли новые строки
        if new_row_count > current_row_count:
            # Обрабатываем только новые строки
            for i in range(current_row_count, new_row_count):
                row = rows[i]
                # Если строка обработана успешно, обновляем current_row_count
                if process_row_window(i + 1, row):
                    current_row_count = i + 1  # Учитываем последнюю успешную строку

        # Ждем 5 минут перед следующим запросом
        time.sleep(300)

if __name__ == "__main__":
    monitor_new_rows()
