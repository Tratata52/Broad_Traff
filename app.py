import logging
import secrets
import sqlite3

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response

from config.config import WORKSHEET1, WORKSHEET2, WORKSHEET3, WORKSHEET4, WORKSHEET5, DB_FILE, DB_FILE_users, \
    WORKSHEET6, WORKSHEET7, WORKSHEET8, WORKSHEET9
from integration_for_amocrm.approw_leads_for_crm import process_row
from requests_to_db import get_db_connection, get_duplicates, save_comment
from send_lead_to_tables import send_lead_to_table_bath, send_lead_to_table_mk_group, send_lead_table_standart

logging.basicConfig(filename='ADMINKA/logs/app_process.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Генерация 32-символьного ключа


# Функция для проверки, авторизован ли пользователь
def login_required(func):
    def wrapper(*args, **kwargs):
        if 'manager_id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


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


@app.route('/report', methods=['GET'])
@login_required  # Проверка авторизации
def report():
    manager_id = session.get('manager_id')

    # Проверка, является ли пользователь администратором
    conn_users = sqlite3.connect(DB_FILE_users)
    cursor_users = conn_users.cursor()
    cursor_users.execute("SELECT admin FROM users WHERE user_id = ?", (manager_id,))
    is_admin = cursor_users.fetchone()
    conn_users.close()

    if is_admin and is_admin[0] == 1:
        # Администратор имеет доступ к отчету
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT manager_name, COUNT(*) AS total_calls, 
                   SUM(CASE WHEN is_sent = 1 THEN 1 ELSE 0 END) AS sent_calls,
                   SUM(CASE WHEN approve = 1 THEN 1 ELSE 0 END) AS approved_calls,
                   SUM(CASE WHEN is_sent = 0 AND approve = 0 THEN 1 ELSE 0 END) AS sent_and_approved
            FROM calls
            GROUP BY manager_name
        """)
        report_data = cursor.fetchall()
        conn.close()

        return render_template('report.html', report_data=report_data)
    else:
        return redirect(url_for('index'))  # Если не администратор, перенаправить на главную


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
        comment = request.form.get('customer_name')
        save_comment(call_id, client_name, comment)

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
@login_required
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
        if project_id == "11962":  # бани
            send_lead_to_table_bath(call, WORKSHEET1)
        elif project_id == "11766":  # двери
            send_lead_to_table_mk_group(call, WORKSHEET2)
        elif project_id == "12112":  # окна
            send_lead_table_standart(call, WORKSHEET3)
        elif project_id == "12206":  # пенопласт
            send_lead_table_standart(call, WORKSHEET4)
        elif project_id == "12205":  # ваша буква
            send_lead_table_standart(call, WORKSHEET5)
        elif project_id == '12257':
            send_lead_table_standart(call, WORKSHEET6)
        elif project_id == '12258':
            send_lead_table_standart(call, WORKSHEET7)
        elif project_id == '12264':
            send_lead_table_standart(call, WORKSHEET8)
        elif project_id == '12265':
            send_lead_table_standart(call, WORKSHEET9)

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


@app.route('/delete/<int:call_id>', methods=['DELETE'])
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
@login_required
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

            audio = row[14]  # mp3_url

            if not note or not note.strip():
                return make_response('Сохраните изменения', 400)

            # Отправляем данные в CRM
            try:
                process_row(name, phone, project_name, manager_name, audio, note)

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
@login_required
def save_data():
    data = request.get_json()
    call_id = data.get('id')
    name_note = data.get('name_note')
    comment = data.get('note')

    # Вызываем функцию для сохранения данных
    try:
        save_comment(call_id, name_note, comment)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/rep')
@login_required
def leads_page():
    return render_template('analisys.html')  # Новая страница с фильтрами и таблицей


if __name__ == '__main__':
    app.run(debug=True)
