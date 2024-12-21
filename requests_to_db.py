# Функция для подключения к базе данных
import logging
import sqlite3

from flask import session

from ADMINKA.config.config import DB_FILE, DB_FILE_users, DB_FILE_analytics


# Инициализация базы данных для звонков
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Создаем таблицу calls, если она не существует
    cursor.execute('''CREATE TABLE IF NOT EXISTS calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        user_id INTEGER,
                        manager_name TEXT,
                        project_id TEXT,
                        project_name TEXT,
                        client_name TEXT,
                        city TEXT,
                        customer_name TEXT,
                        phone TEXT,
                        comment TEXT,
                        note TEXT,
                        name_note TEXT,
                        city_note TEXT,
                        mp3_url TEXT)''')

    # Проверяем, существует ли столбец is_sent в таблице calls
    cursor.execute("PRAGMA table_info(calls)")
    columns = [column[1] for column in cursor.fetchall()]

    # Добавляем столбец is_sent, если он не существует
    if 'is_sent' not in columns:
        cursor.execute('''ALTER TABLE calls ADD COLUMN is_sent BOOLEAN DEFAULT 0''')
        print("Добавлен столбец is_sent")

    if 'approve' not in columns:
        cursor.execute('''ALTER TABLE calls ADD COLUMN approve BOOLEAN DEFAULT 0''')
        print("Добавлен столбец approve")

    else:
        print("Столбец is_sent уже существует")

    conn.commit()
    conn.close()


# подключение к бд
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)  # Имя вашей базы данных
    conn.row_factory = sqlite3.Row
    return conn


# Сохранение данных звонка в базу данных
def add_to_database(date, user_id, manager_name, project_id, project_name, client_name, city, customer_name, phone,
                    comment, mp3_url):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO calls (date, user_id, manager_name, project_id, project_name, client_name, city, customer_name, phone, comment, mp3_url)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (date, user_id, manager_name, project_id, project_name, client_name, city, customer_name, phone,
                    comment, mp3_url))

    conn.commit()
    conn.close()
    logging.info(f"Добавлен звонок в БД: {customer_name}, {phone}, {manager_name}, {project_name}, mp3_url: {mp3_url}")


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
def save_comment(call_id, name, comment):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    query = """
    UPDATE calls 
    SET name_note = ?, note = ? 
    WHERE id = ?
    """

    # Исправляем порядок параметров
    cursor.execute(query, (name, comment, call_id))

    conn.commit()
    conn.close()


# Функция для получения списка user_id из базы данных
def get_user_ids():
    conn = sqlite3.connect(DB_FILE_users)
    cursor = conn.cursor()

    # Получаем все user_id из таблицы users
    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]

    conn.close()
    return user_ids

# создание базы для аналитики

def init_db_analytics():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='logs/analytics.log',
        encoding='UTF-8'
    )

    # Поля таблицы для динамического управления
    TRAFFIC_TABLE_COLUMNS = [
        ('id', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
        ('date_load_base', 'TEXT'),
        ('date_call', 'TEXT'),
        ('project_id', 'INTEGER'),
        ('project_name', 'TEXT'),
        ('contact_base_id', 'INTEGER'),
        ('contact_name', 'TEXT'),
        ('contact_description', 'TEXT'),
        ('contact_id', 'INTEGER'),
        ('id_call', 'INTEGER'),
        ('call_result_id', 'INTEGER'),
        ('contact_status_name', 'TEXT'),
        ('called_phone', 'TEXT'),
        ('name_respond', 'TEXT'),
        ('remark', 'TEXT'),
        ('user_id', 'INTEGER'),
        ('operator_name', 'TEXT'),
        ('is_marriage', 'BOOLEAN DEFAULT 0')
    ]

    """Инициализация базы данных и динамическое создание таблицы."""
    try:
        conn = sqlite3.connect(DB_FILE_analytics)
        cursor = conn.cursor()

        # Динамическое создание таблицы
        columns_definition = ', '.join([f"{name} {type}" for name, type in TRAFFIC_TABLE_COLUMNS])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS traffic ({columns_definition})")
        logging.info("Таблица traffic проверена/создана успешно")

        # Проверка и добавление недостающих столбцов
        cursor.execute("PRAGMA table_info(traffic)")
        existing_columns = {column[1] for column in cursor.fetchall()}

        for name, type in TRAFFIC_TABLE_COLUMNS:
            if name not in existing_columns:
                cursor.execute(f"ALTER TABLE traffic ADD COLUMN {name} {type}")
                logging.info(f"Добавлен столбец: {name} ({type})")

        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")
    finally:
        if conn:
            conn.close()


def add_to_database_analytics(**kwargs):
    """Добавление записи в таблицу traffic."""
    try:
        conn = sqlite3.connect(DB_FILE_analytics)
        cursor = conn.cursor()

        # Формируем запрос с учётом переданных данных
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?' for _ in kwargs])
        values = tuple(kwargs.values())

        cursor.execute(f"INSERT INTO traffic ({columns}) VALUES ({placeholders})", values)
        conn.commit()
        logging.info(f"Добавлена запись: {kwargs}")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при добавлении данных в базу: {e}")
    finally:
        if conn:
            conn.close()

#

#
