import logging
import os
import time
from datetime import datetime

import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

from approw_leads_for_crm import token_bt_crm

# Создание директории для логов, если она не существует
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка логирования

logging.basicConfig(filename=os.path.join(log_dir, 'email_monitor.log'), level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

json_keyfile = 'logical-air-353619-d959f6958ff1.json'

# Файл для хранения последнего обработанного ID сделки
LAST_LEAD_ID_FILE = "last_lead_id.txt"


# Авторизация в Google Sheets
def authorize_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    return client


# Заголовки для авторизации в AmoCRM
headers = {
    'Authorization': f'Bearer {token_bt_crm}',
    'Content-Type': 'application/json'
}

# Константы для домена и ID воронки/статуса
DOMAIN = "infoboardtraffru.amocrm.ru"
PIPELINE_ID = "8701282"  # ID воронки
STATUS_ID = "70487718"  # ID статуса


# Получение последнего обработанного ID сделки
def get_last_lead_id():
    try:
        with open(LAST_LEAD_ID_FILE, 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return None
    except ValueError:
        logging.error("Ошибка чтения последнего ID сделки из файла.")
        return None


# Сохранение последнего ID сделки
def save_last_lead_id(lead_id):
    with open(LAST_LEAD_ID_FILE, 'w') as file:
        file.write(str(lead_id))


# Получение сделок
def get_leads(pipeline_id, status_id):
    api_url = f"https://{DOMAIN}/api/v4/leads?filter[pipeline]={pipeline_id}&filter[status]={status_id}"
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json().get('_embedded', {}).get('leads', [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении сделок: {e}")
        return []


# Получение примечаний
def get_lead_notes(lead_id):
    api_url_notes = f"https://{DOMAIN}/api/v4/leads/{lead_id}/notes"
    try:
        notes_response = requests.get(api_url_notes, headers=headers)
        notes_response.raise_for_status()
        notes = notes_response.json()

        note_texts = []
        if '_embedded' in notes and 'notes' in notes['_embedded']:
            for note in notes['_embedded']['notes']:
                note_text = note['params'].get('text', 'Нет текста')
                note_texts.append(note_text)
        return note_texts
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении примечаний для сделки {lead_id}: {e}")
        return []


# Извлечение данных о сделке
def extract_lead_data(lead):
    name = lead['name']
    phone, comment, project_id, name_manager = None, None, None, None

    for field in lead.get('custom_fields_values', []):
        if field['field_name'] == 'Дополнительные комментарии':
            comment = field['values'][0]['value']
        elif field['field_name'] == 'Телефон клиента':
            phone = field['values'][0]['value']
        elif field['field_name'] == 'Id проекта':
            project_id = field['values'][0]['value']


        elif field['field_name'] == 'Имя оператора':
            name_manager = field['values'][0]['value']

    logging.info(
        f"Извлеченные данные: Имя - {name}, Телефон - {phone}, Комментарий - {comment}, "
        f"Id проекта - {project_id},  Имя оператора - {name_manager}")

    return name, phone, comment, project_id, name_manager


# Запись данных в Google Sheet бани
def write_to_google_sheet_bath(sheet, name, phone, notes_text):
    current_date = datetime.now().strftime("%d.%m.%Y")  # Получение текущей даты
    row_data = [current_date, name, phone, None, notes_text]
    sheet.insert_row(row_data, index=len(sheet.get_all_values()) + 1)
    logging.info(f"Добавлена строка: Дата - {current_date}, Имя - {name}, Телефон - {phone}, Примечания - {notes_text}")


# Запись данных в Google Sheet двери
def write_to_google_sheet_mk_group(sheet, name, phone, notes_text, name_manager):
    current_date = datetime.now().strftime("%d.%m.%Y")
    current_time = datetime.now().strftime('%H:%M')
    # Данные для добавления
    row_data = [current_date, current_time, name, phone, None, notes_text, None, None, None, None, None, None,
                name_manager]
    # Вставляем строку в начало (после заголовков) и всегда с колонки A
    sheet.insert_row(row_data, index=len(
        sheet.get_all_values()) + 1)  # Определяет длину текущих строк и вставляет ниже последней строки
    logging.info(f"Добавлена строка: Дата - {current_date}, Имя - {name}, Телефон - {phone}, Примечания - {notes_text}")


# Основная функция для проверки новых сделок
def check_for_new_leads(client):
    # Тест
    # spreadsheet_bath = client.open_by_url(
    #     'https://docs.google.com/spreadsheets/d/1KXfLGJmA0lfirmK7Zslcl3XM2-30k2cHzqXQ_FuswRM/edit?gid=4684822#gid=4684822')
    # spreadsheet_mk = client.open_by_url(
    #     'https://docs.google.com/spreadsheets/d/1KXfLGJmA0lfirmK7Zslcl3XM2-30k2cHzqXQ_FuswRM/edit?gid=4684822#gid=4684822')

    #Таблицы клиентов
    spreadsheet_bath = client.open_by_url(
            'https://docs.google.com/spreadsheets/d/1-gV-0zTNFVMpYrVeZHvsLsHBAbTX5hfJZClsOhizKoI/edit?gid=506524704#gid=506524704')
    spreadsheet_mk = client.open_by_url(
            'https://docs.google.com/spreadsheets/d/1nj3nz6rXhWI0QS_Qp_ujYsy8zTByb94VDDyDRkSKDv0/edit?gid=2050218078#gid=2050218078')

    # Получаем последний ID сделки или устанавливаем его на 0, если он не найден
    last_lead_id = get_last_lead_id() or 0
    leads = get_leads(PIPELINE_ID, STATUS_ID)
    if not leads:
        logging.info("Сделки не найдены.")
        return

    # Отфильтровываем сделки по последнему ID
    leads = sorted([lead for lead in leads if lead['id'] > last_lead_id], key=lambda x: x['id'])
    logging.info(f"Найдено {len(leads)} новых сделок для обработки.")

    if not leads:
        logging.info("Новых сделок для обработки нет.")
        return

    # Обработка сделок
    for lead in leads:
        lead_id = lead['id']
        name, phone, comment, project_id, name_manager = extract_lead_data(lead)
        notes = get_lead_notes(lead['id'])
        notes_text = "\n".join(notes)

        if project_id == '11766' and name and phone:
            sheet = spreadsheet_mk.get_worksheet(0)
            write_to_google_sheet_mk_group(sheet, name, phone, notes_text, name_manager)
        elif project_id == '11962' and name and phone:
            sheet2 = spreadsheet_bath.get_worksheet(0)
            write_to_google_sheet_bath(sheet2, name, phone, notes_text)
        else:
            logging.warning(f"Пропуск сделки ID {lead_id} - неизвестный ID проекта или отсутствие данных.")
            continue

    # Сохраняем последний обработанный ID сделки
    latest_processed_id = leads[-1]['id']
    save_last_lead_id(latest_processed_id)
    logging.info(f"Последний обработанный ID сделки: {latest_processed_id}")


def main():
    client = authorize_google_sheets()

    while True:
        check_for_new_leads(client)
        logging.info("Пауза на 2 минуты перед следующим запросом.")
        time.sleep(120)  # Ожидание 2 минуты (120 секунд)


if __name__ == "__main__":
    main()
