import json
import time
import traceback
import requests
from ADMINKA.config.config import WORKSHEET1, WORKSHEET9
from ADMINKA.config.config import headers

url = 'https://amomail.amocrm.ru/api/v2/31780414/messages/send'

# Хранение количества строк в таблицах
row_counts = {
    "WORKSHEET1": len(WORKSHEET1.get_all_values()),
    "WORKSHEET9": len(WORKSHEET9.get_all_values())
}

# Универсальная функция для отправки писем
def send_email(email, mailbox_id, subject, message_text):
    try:
        data_form = {
            "subject": subject,
            "attachments": {},
            "content_type": "html",
            "content": f"<div>{message_text}</div>",
            "template_fields": {"profile.name": "Илья", "profile.phone": "null"},
            "from": {"mailbox_id": mailbox_id, "name": "Илья"},
            "to": [{"email": email, "name": ""}]
        }

        response = requests.post(url, headers=headers, data=json.dumps(data_form))
        if response.status_code == 202:
            return True
        else:
            print(f"Ошибка отправки письма: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")
        traceback.print_exc()
        return False

# Обработка строки для первой таблицы (WORKSHEET1)
def process_row_window(row_number, row):
    try:
        name = row[1] if len(row) > 1 else ""
        phone = row[0] if len(row) > 0 else ""
        comment = row[2] if len(row) > 2 else ""

        if not (name and phone and comment):
            print(f"Пропущена строка {row_number}: Не хватает данных (имя, телефон, комментарий).")
            return False

        message_text = f"{phone}<br>{name}<br>{comment}"
        subject = "Лид ВТ"
        return send_email("kval@ekobany.ru", "151359", subject, message_text)
    except Exception as e:
        print(f"Ошибка при обработке строки {row_number}: {e}")
        traceback.print_exc()
        return False

# Обработка строки для второй таблицы (WORKSHEET9)
def process_row_car(row_number, row):
    try:
        name = row[2] if len(row) > 2 else ""
        phone = row[1] if len(row) > 1 else ""
        comment = row[3] if len(row) > 3 else ""

        if not (name and phone and comment):
            print(f"Пропущена строка {row_number}: Не хватает данных (имя, телефон, комментарий).")
            return False

        message_text = f"{phone}<br>{name}<br>{comment}"
        subject = "Лид ВТ"
        return send_email("business@topcar-elite.ru", "151359", subject, message_text)
    except Exception as e:
        print(f"Ошибка при обработке строки {row_number}: {e}")
        traceback.print_exc()
        return False

# Обработка новой таблицы
def process_table(worksheet, table_key, process_row_function):
    global row_counts
    try:
        rows = worksheet.get_all_values()
        new_row_count = len(rows)

        if new_row_count > row_counts[table_key]:
            for i in range(row_counts[table_key], new_row_count):
                row = rows[i]
                if process_row_function(i + 1, row):
                    row_counts[table_key] = i + 1
    except Exception as e:
        print(f"Ошибка при обработке таблицы {table_key}: {e}")
        traceback.print_exc()

# Основной процесс мониторинга
def monitor_new_rows():
    while True:
        try:
            # Обрабатываем первую таблицу
            process_table(WORKSHEET1, "WORKSHEET1", process_row_window)
            # Обрабатываем вторую таблицу
            process_table(WORKSHEET9, "WORKSHEET9", process_row_car)
            # Ждем 5 минут перед следующим запросом
            time.sleep(300)
        except Exception as e:
            print(f"Ошибка в мониторинге: {e}")
            traceback.print_exc()
            print("Перезапуск мониторинга через 10 секунд...")
            time.sleep(10)

if __name__ == "__main__":
    while True:
        try:
            monitor_new_rows()
        except Exception as e:
            print(f"Критическая ошибка в основном цикле: {e}")
            traceback.print_exc()
            print("Перезапуск скрипта через 10 секунд...")
            time.sleep(10)
