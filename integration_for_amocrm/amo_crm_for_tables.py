from approw_leads_for_crm import token_bt_crm
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time
import os
import logging


# Создание директории для логов, если она не существует
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настройка логирования
logging.basicConfig(filename=os.path.join(log_dir, 'amo_table.log'), level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
    phone = None
    comment = None
    project_id = None

    for field in lead.get('custom_fields_values', []):
        if field['field_name'] == 'Дополнительные комментарии':
            comment = field['values'][0]['value']
        elif field['field_name'] == 'Телефон клиента':
            phone = field['values'][0]['value']
        elif field['field_name'] == 'Id проекта':  # Извлечение id_проекта
            project_id = field['values'][0]['value']
        elif field['field_name'] == 'Город':  # Извлечение id_проекта
            project_id = field['values'][0]['value']

    logging.info(f"Извлеченные данные: Имя - {name}, Телефон - {phone}, Комментарий - {comment}, Id проекта - {project_id}")
    return name, phone, comment, project_id  # Возвращаем id_проекта

# Запись данных в Google Sheet
def write_to_google_sheet(sheet, name, phone, city, notes_text ):
    current_date = datetime.now().strftime("%d.%m.%Y")  # Получение текущей даты
    sheet.append_row([current_date, name, phone,city, notes_text])  # Добавляем текущую дату в первый столбец
    logging.info(f"Добавлена строка: Дата - {current_date}, Имя - {name}, Телефон - {phone}, Примечания - {notes_text}")

# Основная функция для проверки новых сделок
def check_for_new_leads(client):
    spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1KXfLGJmA0lfirmK7Zslcl3XM2-30k2cHzqXQ_FuswRM/edit?gid=161808248#gid=161808248')

    # Получаем последний обработанный ID сделки
    last_lead_id = get_last_lead_id()
    logging.info(f"Последний обработанный ID сделки: {last_lead_id}")

    # Получаем сделки из AmoCRM
    leads = get_leads(PIPELINE_ID, STATUS_ID)
    if not leads:
        logging.info("Сделки не найдены.")
        return

    # Обратный порядок для обработки от самых новых к старым
    leads.sort(key=lambda x: x['id'], reverse=True)

    for lead in leads:
        lead_id = lead['id']
        if last_lead_id is None or lead_id > last_lead_id:
            name, phone, comment, project_id = extract_lead_data(lead)
            notes = get_lead_notes(lead['id'])
            notes_text = "\n".join(notes)

            if project_id == '11766':
                sheet = spreadsheet.get_worksheet(0)  # Открываем первую таблицу для проекта 11766
            elif project_id == '11962':
                sheet = spreadsheet.get_worksheet(1)  # Открываем вторую таблицу для проекта 11962
            else:
                logging.warning(f"Неизвестный ID проекта {project_id}. Пропуск сделки.")
                continue

            if name and phone and comment:
                write_to_google_sheet(sheet, name, phone, notes_text)
                save_last_lead_id(lead_id)  # Сохраняем последний ID сделки
            else:
                logging.warning(f"Пропущена сделка с ID {lead_id} из-за отсутствия необходимых данных.")
        else:
            logging.info(f"Сделка с ID {lead_id} уже была обработана.")

def main():
    client = authorize_google_sheets()

    while True:
        check_for_new_leads(client)
        logging.info("Пауза на 2 минуты перед следующим запросом.")
        time.sleep(120)  # Ожидание 2 минуты (120 секунд)

if __name__ == "__main__":
    main()
