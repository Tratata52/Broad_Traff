import json
import time

import requests

from ADMINKA.config.config import WORKSHEET1
from ADMINKA.config.config import headers

url = 'https://amomail.amocrm.ru/api/v2/31780414/messages/send'

# Инициализируем переменную для хранения последнего числа строк
current_row_count = len(WORKSHEET1.get_all_values())


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
        "to": [{"email": "kval@ekobany.ru", "name": ""}]
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
        rows = WORKSHEET1.get_all_values()
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
