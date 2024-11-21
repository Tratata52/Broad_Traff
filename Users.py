import logging
import os
import sqlite3
import time  # Для паузы в 12 часов

import requests

from config.config import API_KEY, USERS_URL

DB_FILE = 'user_data.db'

# Создаём папку logs, если её нет
if not os.path.exists('logs'):
    os.makedirs('logs')

# Настраиваем логирование
logging.basicConfig(filename='logs/users_process.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Удаляем таблицу, если она существует
    cursor.execute('''DROP TABLE IF EXISTS users''')

    # Создаём таблицу заново
    cursor.execute('''CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        operator_name TEXT,
                        email TEXT,
                        admin INTEGER)''')

    conn.commit()
    conn.close()


# Сохранение данных звонка в базу данных
def add_to_database(user_id, operator_name, operator_email, admin_status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users (user_id, operator_name, email, admin)
                      VALUES (?, ?, ?, ?)''',
                   (user_id, operator_name, operator_email, admin_status))  # Добавлено admin_status
    conn.commit()
    conn.close()
    logging.info(f"Добавлен пользователь {operator_name}")


# Получение пользователей
def fetch_and_save_users():
    users_response = requests.get(USERS_URL, headers={"X-API-KEY": API_KEY})

    if users_response.status_code == 200:
        users_data = users_response.json()

        # Проверяем, что данные - это список
        if isinstance(users_data, list) and users_data:
            for user_data in users_data:
                account_enabled = user_data.get('account_enabled', True)
                if account_enabled:
                    user_id = user_data['id']
                    email = user_data['email']
                    name = user_data['name']
                    admin = user_data['admin']

                    # Конвертируем булевое значение в целочисленное
                    admin_status = 1 if admin else 0

                    add_to_database(user_id, name, email, admin_status)

                    print(f"Пользователь добавлен: {name}, Аккаунт включен: {account_enabled}")
        else:
            print("Ошибка: Данные пользователей пусты или не являются списком.")
    else:
        print(f"Ошибка при получении данных пользователей: {users_response.status_code}")


# Основная функция
def main():
    init_db()

    while True:
        # Очищаем или переписываем записи
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)  # Удаляем файл базы данных перед каждым циклом
            init_db()  # Инициализируем базу данных заново

        fetch_and_save_users()  # Получаем и сохраняем данные пользователей

        print("Данные пользователей переписаны")

        time.sleep(6 * 60 * 60)  # 6 часов * 60 минут * 60 секунд


if __name__ == "__main__":
    main()
