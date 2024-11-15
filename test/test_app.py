import logging
import secrets
import sqlite3
from datetime import datetime

import gspread
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from oauth2client.service_account import ServiceAccountCredentials

from integration_for_amocrm.approw_leads_for_crm import process_row

logging.basicConfig(filename='ADMINKA/logs/app_process.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Генерация 32-символьного ключа

# БАЗЫ ДАННЫХ
DB_FILE = '../leads.db'
DB_FILE_users = '../user_data.db'

# Подключение к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
JSON_KEYFILE = 'logical-air-353619-d959f6958ff1.json'
CREDS = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYFILE, SCOPE)
CLIENT = gspread.authorize(CREDS)

# URLs таблиц для различных проектов
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1KXfLGJmA0lfirmK7Zslcl3XM2-30k2cHzqXQ_FuswRM/edit?gid=4684822'  # бани
SPREADSHEET_URL2 = 'https://docs.google.com/spreadsheets/d/1KXfLGJmA0lfirmK7Zslcl3XM2-30k2cHzqXQ_FuswRM/edit?gid=4684822'  # МК групп
SPREADSHEET_URL3 = 'https://docs.google.com/spreadsheets/d/1KXfLGJmA0lfirmK7Zslcl3XM2-30k2cHzqXQ_FuswRM/edit?gid=4684822'  # окна

SPREADSHEET1 = CLIENT.open_by_url(SPREADSHEET_URL)
SPREADSHEET2 = CLIENT.open_by_url(SPREADSHEET_URL2)
SPREADSHEET3 = CLIENT.open_by_url(SPREADSHEET_URL3)

WORKSHEET1 = SPREADSHEET1.get_worksheet(0)  # бани
WORKSHEET2 = SPREADSHEET2.get_worksheet(1)  # МК групп
WORKSHEET3 = SPREADSHEET3.get_worksheet(2)  # окна


# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# Получение всех проектов
def get_projects():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT project_name FROM calls")
    projects = cursor.fetchall()
    conn.close()
    return projects


# Получение звонков
def get_calls(manager_name, project_name):
    conn_call = get_db_connection()
    conn_users = sqlite3.connect(DB_FILE_users)
    cursor_call = conn_call.cursor()
    cursor_users = conn_users.cursor()

    manager_id = session.get('manager_id')
    cursor_users.execute("SELECT admin FROM users WHERE user_id = ?", (manager_id,))
    is_admin = cursor_users.fetchone()

    query = "SELECT * FROM calls WHERE is_sent = 0 AND approve = 0"
    params = []

    if is_admin and is_admin[0] == 1:  # Если администратор
        if manager_name:
            query += " AND manager_name = ?"
            params.append(manager_name)
        if project_name:
            query += " AND project_name = ?"
            params.append(project_name)
    else:
        query += " AND user_id = ?"
        params.append(manager_id)
        if manager_name:
            query += " AND manager_name = ?"
            params.append(manager_name)
        if project_name:
            query += " AND project_name = ?"
            params.append(project_name)

    cursor_call.execute(query, params)
    calls = cursor_call.fetchall()
    conn_call.close()

    phone_count = {}
    for call in calls:
        phone = call[9]
        phone_count[phone] = phone_count.get(phone, 0) + 1

    enriched_calls = [(call + (phone_count[call[9]] > 1,)) for call in calls]
    return enriched_calls


# Получение дублей телефонов
def get_duplicates():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT phone
        FROM calls
        GROUP BY phone
        HAVING COUNT(*) > 1;
    """)

    duplicates = [row[0] for row in cursor.fetchall()]
    connection.close()
    return duplicates


# Сохранение комментария и примечания
def save_comment(call_id, name, comment):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    UPDATE calls 
    SET note = ?, name_note = ?
    WHERE id = ?
    """
    cursor.execute(query, (name, comment, call_id))
    conn.commit()
    conn.close()


# Функции для отправки лида в Google Sheets
def send_lead_to_table_bath(call, WORKSHEET):
    current_date = datetime.now().strftime("%d.%m.%Y")
    row = [call[12], call[9], call[11]]
    try:
        WORKSHEET.append_row(row, value_input_option='RAW', insert_data_option='INSERT_ROWS')
        logging.info(f"Успешно добавлена строка: {row}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении строки в таблицу: {e} | Данные: {row}")


def send_lead_to_table_mk_group(call, WORKSHEET):
    current_date = datetime.now().strftime("%d.%m")
    current_time = datetime.now().strftime('%H:%M')

    row = [current_date, current_time, call[12], call[9], " ", call[11], " ", " ", " ", " ", " ", " ", call[3]]
    try:
        WORKSHEET.append_row(row, value_input_option='RAW', insert_data_option='INSERT_ROWS')
        logging.info(f"Успешно добавлена строка: {row}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении строки в таблицу: {e} | Данные: {row}")


def send_lead_table_window(call, WORKSHEET):
    current_date = datetime.now().strftime("%d.%m.%Y")
    row = [current_date, call[12], call[9], call[11]]
    try:
        WORKSHEET.append_row(row, value_input_option='RAW', insert_data_option='INSERT_ROWS')
        logging.info(f"Успешно добавлена строка: {row}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении строки в таблицу: {e} | Данные: {row}")


# Проверка авторизации
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'manager_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


# Авторизация
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        manager_id = request.form.get('user_id')

        if not manager_id:
            error_message = "ID менеджера не может быть пустым."
            return render_template('login.html', error=error_message)

        conn = sqlite3.connect(DB_FILE_users)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, operator_name FROM users WHERE user_id = ?", (manager_id,))
        manager = cursor.fetchone()
        conn.close()

        if manager:
            session['manager_id'] = manager[0]
            session['manager_name'] = manager[1]
            return redirect(url_for('index'))
        else:
            error_message = "Неверный ID менеджера. Попробуйте снова."
            return render_template('login.html', error=error_message)

    return render_template('login.html')


# Главная страница
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    current_theme = request.args.get('current_theme', 'css/white_styles.css')
    manager_id = session.get('manager_id')

    conn_users = sqlite3.connect(DB_FILE_users)
    cursor_users = conn_users.cursor()
    cursor_users.execute("SELECT admin FROM users WHERE user_id = ?", (manager_id,))
    is_admin = cursor_users.fetchone()
    conn_users.close()

    if request.method == 'POST':
        call_id = request.form.get('id')
        client_name = request.form.get('client_name')
        comment = request.form.get('customer_name')
        save_comment(call_id, comment, client_name)

    conn = get_db_connection()
    cursor = conn.cursor()

    if is_admin and is_admin[0] == 1:
        cursor.execute("SELECT DISTINCT manager_name FROM calls")
        managers = cursor.fetchall()
    else:
        managers = []

    cursor.execute("SELECT DISTINCT project_name FROM calls")
    projects = cursor.fetchall()

    if is_admin and is_admin[0] == 1:
        calls = get_calls(None, None)
    else:
        calls = get_calls(session['manager_name'], None)

    conn.close()
    return render_template("index.html", calls=calls, projects=projects, managers=managers, current_theme=current_theme)


if __name__ == '__main__':
    app.run(debug=True)
