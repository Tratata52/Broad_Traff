import logging
import secrets
import sqlite3
from datetime import datetime

import gspread
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from oauth2client.service_account import ServiceAccountCredentials


from ADMINKA.integration_for_amocrm.approw_leads_for_crm import process_row

logging.basicConfig(filename='ADMINKA/logs/app_process.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Генерация 32-символьного ключа

# БАЗЫ ДАННЫХ
DB_FILE = 'test/leads.db'
DB_FILE_users = 'test/user_data.db'

# Подключение к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
JSON_KEYFILE = 'logical-air-353619-d959f6958ff1.json'

CREDS = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYFILE, SCOPE)
CLIENT = gspread.authorize(CREDS)
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1KXfLGJmA0lfirmK7Zslcl3XM2-30k2cHzqXQ_FuswRM/edit?gid=4684822'  # бани
SPREADSHEET_URL2 = 'https://docs.google.com/spreadsheets/d/1KXfLGJmA0lfirmK7Zslcl3XM2-30k2cHzqXQ_FuswRM/edit?gid=4684822'  # МК групп
SPREADSHEET1 = CLIENT.open_by_url(SPREADSHEET_URL)
SPREADSHEET2 = CLIENT.open_by_url(SPREADSHEET_URL2)
WORKSHEET1 = SPREADSHEET1.get_worksheet(0)  # бани
WORKSHEET2 = SPREADSHEET2.get_worksheet(1)  # МК групп


# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)  # Имя вашей базы данных
    conn.row_factory = sqlite3.Row
    return conn

# Получение всех проектов
def get_projects():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT project_name FROM calls")
    projects = cursor.fetchall()
    conn.close()
    return projects

# Получение звонков
def get_calls(manager_name, project_name):
    conn_call = sqlite3.connect(DB_FILE)
    conn_users = sqlite3.connect(DB_FILE_users)
    cursor_call = conn_call.cursor()
    cursor_users = conn_users.cursor()

    # Получение информации о текущем пользователе
    manager_id = session.get('manager_id')
    cursor_users.execute("SELECT admin FROM users WHERE user_id = ?", (manager_id,))
    is_admin = cursor_users.fetchone()

    # Начало формирования запроса
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
        # Если не администратор, добавляем условие для фильтрации по user_id
        query += " AND user_id = ?"
        params.append(manager_id)  # Здесь используем manager_id как user_id
        if manager_name:
            query += " AND manager_name = ?"
            params.append(manager_name)
        if project_name:
            query += " AND project_name = ?"
            params.append(project_name)

    cursor_call.execute(query, params)
    calls = cursor_call.fetchall()
    conn_call.close()

    # Обработка звонков
    phone_count = {}
    for call in calls:
        phone = call[9]
        phone_count[phone] = phone_count.get(phone, 0) + 1

    enriched_calls = [(call + (phone_count[call[9]] > 1,)) for call in calls]
    return enriched_calls

# Получение дублей телефонов
def get_duplicates():
    connection = sqlite3.connect(DB_FILE)  # Укажите путь к вашей базе данных
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


# Сохранение комментария и примечания в базе данных
def save_comment(call_id, name, city, comment):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = """
    UPDATE calls 
    SET name_note = ?, city_note = ?, note = ?
    WHERE id = ?
    """

    # Исправляем порядок параметров
    cursor.execute(query, (name, city, comment, call_id))

    conn.commit()
    conn.close()


# Отправка лида в Google Sheets
def send_lead_to_table(call, WORKSHEET):
    current_date = datetime.now().strftime("%d.%m.%Y")
    row = [current_date, call[12], call[9], call[13], call[11]]
    try:
        WORKSHEET.append_row(row, value_input_option='RAW', insert_data_option='INSERT_ROWS')
        logging.info(f"Успешно добавлена строка: {row}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении строки в таблицу: {e} | Данные: {row}")


# Функция для проверки, авторизован ли пользователь
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

        # Проверка manager_id в базе данных
        conn = sqlite3.connect(DB_FILE_users)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, operator_name FROM users WHERE user_id = ?", (manager_id,))
        manager = cursor.fetchone()
        conn.close()

        if manager:  # Если менеджер найден
            session['manager_id'] = manager[0]  # Сохраняем manager_id в сессии
            session['manager_name'] = manager[1]  # Сохраняем manager_name в сессии
            return redirect(url_for('index'))  # Перенаправляем на главную страницу
        else:
            error_message = "Неверный ID менеджера. Попробуйте снова."
            return render_template('login.html', error=error_message)

    return render_template('login.html')  # Страница входа

# Главная страница
@app.route('/', methods=['GET', 'POST'])
@login_required  # Проверка сессии перед доступом к главной странице
def index():
    # Устанавливаем значение темы по умолчанию
    current_theme = request.args.get('current_theme', 'css/white_styles.css')

    manager_id = session.get('manager_id')

    # Проверяем, является ли пользователь администратором
    conn_users = sqlite3.connect(DB_FILE_users)
    cursor_users = conn_users.cursor()
    cursor_users.execute("SELECT admin FROM users WHERE user_id = ?", (manager_id,))
    is_admin = cursor_users.fetchone()
    conn_users.close()

    if request.method == 'POST':
        call_id = request.form.get('id')
        client_name = request.form.get('client_name')
        city = request.form.get('city')
        comment = request.form.get('comment')
        save_comment(call_id, client_name, city, comment)

    # Получаем список менеджеров и проектов
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if is_admin and is_admin[0] == 1:  # Если пользователь администратор
        cursor.execute("SELECT DISTINCT manager_name FROM calls")
        managers = cursor.fetchall()
    else:
        managers = []  # Пустой список, если не администратор

    cursor.execute("SELECT DISTINCT project_name FROM calls")
    projects = cursor.fetchall()
    conn.close()

    selected_manager = request.args.get('manager')  # Получаем выбранного менеджера
    selected_project = request.args.get('project')  # Получаем выбранный проект

    # Теперь мы передаем аргументы в get_calls
    calls = get_calls(selected_manager, selected_project)
    duplicates = get_duplicates()  # Получаем дубликаты

    # Убедитесь, что current_theme правильно передается в шаблон
    return render_template(
        'index.html',
        calls=calls,  # Передаем отфильтрованные звонки
        duplicates=duplicates,
        managers=managers,
        projects=projects,
        selected_manager=selected_manager,
        selected_project=selected_project,
        is_admin=is_admin and is_admin[0] == 1,
        current_theme=current_theme
    )


@app.route('/send/<int:call_id>', methods=['POST'])
def send_lead(call_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM calls WHERE id = ?", (call_id,))
    call = cursor.fetchone()
    project_id = call[4]
    note = call[11]
    if not note or not note.strip():
        return make_response('Сохраните изменения', 400)

    try:
        if project_id == "11962":
            send_lead_to_table(call, WORKSHEET1)
        elif project_id == "11766":
            send_lead_to_table(call, WORKSHEET2)
        else:

            return make_response('Неизвестный проект', 400)

        cursor.execute("UPDATE calls SET is_sent = 1, approve = 0 WHERE id = ?", (call_id,))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Данные успешно отправлены!'}), 200
    except Exception as e:
        logging.error(f"Ошибка при отправке данных: {e}")
        return make_response('Ошибка при обработке данных', 500)
    finally:
        cursor.close()
        conn.close()

@app.route('/delete/<int:call_id>', methods=['POST'])
@login_required
def delete_call(call_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Проверка, существует ли запись с таким ID
        cursor.execute("SELECT * FROM calls WHERE id = ?", (call_id,))
        if cursor.fetchone() is None:
            logging.warning(f"Звонок с ID {call_id} не найден.")
            return jsonify({"status": "error", "message": "Звонок не найден"}), 404

        cursor.execute("DELETE FROM calls WHERE id = ?", (call_id,))
        conn.commit()
        logging.info(f"Звонок с ID {call_id} был удалён.")
        return jsonify({"status": "success"})
    except sqlite3.Error as e:
        logging.error(f"Ошибка при удалении звонка: {e}")
        return jsonify({"status": "error", "message": "Не удалось удалить звонок"}), 500
    except Exception as e:
        logging.error(f"Общая ошибка: {e}")
        return jsonify({"status": "error", "message": "Не удалось удалить звонок"}), 500
    finally:
        conn.close()



@app.route('/logout')
@login_required
def logout():
    session.pop('manager_id', None)  # Удаляем manager_id из сессии
    return redirect(url_for('login'))  # Перенаправляем на страницу входа


@app.route('/approve', methods=['POST'])
def approve():
    data = request.json
    row_id = data.get('id')  # Получаем ID строки

    # Подключаемся к базе данных и извлекаем нужные данные по ID
    conn = get_db_connection()  # Открываем соединение
    try:
        row = conn.execute('SELECT * FROM calls WHERE id = ?', (row_id,)).fetchone()

        if row:
            # Извлекаем данные из строки по индексам
            phone = row[9]  # phone
            project_name = row[4]  # project_id
            manager_name = row[3]  # manager_name
            note = row[11]  # note
            name = row[12]  # name_note
            city = row[13]  # city_note
            audio = row[14]  # mp3_url

            if not note or not note.strip():
                return make_response('Сохраните изменения', 400)

            # Отправляем данные в CRM
            try:
                process_row(name, city, phone, project_name, manager_name, audio, note)

                # Обновляем approve на 1 и оставляем is_sent = 0
                conn.execute("UPDATE calls SET approve = 1, is_sent = 0 WHERE id = ?", (row_id,))
                conn.commit()

                return jsonify({'status': 'success'}), 200
            except Exception as e:
                print(f"Ошибка при отправке данных в CRM: {e}")
                return jsonify({'status': 'error', 'message': str(e)}), 500
        else:
            return jsonify({'status': 'error', 'message': 'Строка не найдена'}), 404
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()  # Закрываем соединение в finally блоке





@app.route('/save_lead', methods=['POST'])
def save_data():
    data = request.get_json()
    call_id = data.get('id')
    name_note = data.get('name_note')
    city_note = data.get('city_note')
    comment = data.get('note')

    # Вызываем функцию для сохранения данных
    try:
        save_comment(call_id, name_note, city_note, comment)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/reports', methods=['GET'])
@login_required
def reports():
    manager_id = session.get('manager_id')

    # Проверяем, является ли пользователь администратором
    conn_users = sqlite3.connect(DB_FILE_users)
    cursor_users = conn_users.cursor()
    cursor_users.execute("SELECT admin FROM users WHERE user_id = ?", (manager_id,))
    is_admin = cursor_users.fetchone()
    conn_users.close()

    # Соединение с базой данных звонков
    conn = get_db_connection()
    cursor = conn.cursor()

    # Если админ, выбираем все звонки, иначе только для текущего пользователя
    if is_admin and is_admin[0] == 1:
        query = "SELECT * FROM calls WHERE is_sent = 1 OR approve = 1"
        cursor.execute(query)
    else:
        query = "SELECT * FROM calls WHERE (is_sent = 1 OR approve = 1) AND user_id = ?"
        cursor.execute(query, (manager_id,))

    reports = cursor.fetchall()
    conn.close()

    return render_template('reports.html', reports=reports, is_admin=is_admin and is_admin[0] == 1)


if __name__ == '__main__':
    app.run(debug=True)
