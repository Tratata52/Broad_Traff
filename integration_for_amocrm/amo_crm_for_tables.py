import logging
import os
import time

import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

from ADMINKA.config.config import JSON_KEYFILE, LAST_LEAD_ID_FILE, DOMAIN, PIPELINE_ID, STATUS_ID, WORKSHEET6
from ADMINKA.config.config import WORKSHEET1, WORKSHEET2, WORKSHEET3, WORKSHEET4, WORKSHEET5
from approw_leads_for_crm import headers
from write_to_gsheet import write_to_google_sheet_mk_group, \
    write_to_google_sheet_bath,write_to_google_sheet_stadart

# Создание директории для логов, если она не существует
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка логирования

logging.basicConfig(filename=os.path.join(log_dir, 'email_monitor.log'), level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

json_keyfile = JSON_KEYFILE


# Авторизация в Google Sheets
def authorize_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    return client


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


# Основная функция для проверки новых сделок
def check_for_new_leads(client):
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
            write_to_google_sheet_mk_group(WORKSHEET2, phone, name, notes_text)

        elif project_id == '11962' and name and phone:

            write_to_google_sheet_bath(WORKSHEET1, phone, name, notes_text)
        elif project_id == "12112":
            write_to_google_sheet_stadart(WORKSHEET3, phone, name, notes_text)

        elif project_id == "12206":
            write_to_google_sheet_stadart(WORKSHEET4, phone, name, notes_text)

        elif project_id == "12205":
            write_to_google_sheet_stadart(WORKSHEET5, phone, name, notes_text)

        elif project_id == "12257":
            write_to_google_sheet_stadart(WORKSHEET6, phone, name, notes_text)

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
