import asyncio
import os
import logging
import aiohttp
import re
from datetime import datetime
import logging


from ADMINKA.config.config import API_KEY, CALL_HISTORY_URL, LAST_CALL_ID_FILE, Project_ids
from ADMINKA.requests_to_db import add_to_database_analytics, init_db_analytics

# Создание папки для логов
os.makedirs('logs', exist_ok=True)

# Настройка логирования
logging.basicConfig(
    filename='logs/call_processor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='UTF-8'
)

#
def format_phone_number(phone):
    # Удаляем все символы, кроме цифр
    digits = ''.join(filter(str.isdigit, phone))

    # Проверяем длину номера
    if len(digits) < 10:
        print(f"Некорректный номер: {digits}")
        return "Некорректный номер"

    # Приводим к российскому формату
    if digits.startswith('8'):
        digits = '7' + digits[1:]
    elif not digits.startswith('7'):
        digits = '7' + digits[-10:]  # Добавляем 7 и оставляем последние 10 цифр

    # print(f"Форматированный номер: {digits}")
    return digits

def get_today_date():
    return datetime.now().strftime("%d.%m.%Y")


def read_last_call_id():
    """Чтение последнего обработанного ID."""
    return open(LAST_CALL_ID_FILE).read().strip() if os.path.exists(LAST_CALL_ID_FILE) else None


def write_last_call_id(call_id):
    """Сохранение последнего обработанного ID."""
    with open(LAST_CALL_ID_FILE, 'w') as file:
        file.write(str(call_id))


def extract_custom_field(call, field_name):
    """Извлечение значения кастомного поля."""
    for field in call.get('custom_fields', []):
        if field.get('title') == field_name:
            return field.get('value')
    return None


async def format_date(date_string):
    """Преобразует строку даты в формат д.м.г."""
    try:
        if not date_string or date_string.lower() == 'не указано':
            logging.warning("Пустая или некорректная дата: возвращаю 'Не указано'")
            return 'Не указано'

        # Попытка обработать разные форматы
        if 'T' in date_string:
            # Формат ISO (например, 2024-12-01T07:10:04.489Z)
            cleaned_date = date_string.split('.')[0].replace('T', ' ')
            parsed_date = datetime.strptime(cleaned_date, "%Y-%m-%d %H:%M:%S")
        elif re.match(r'\d{4}-\d{2}-\d{2} \d{1,2}:\d{1,2}:\d{1,2}', date_string):
            # Формат ГГГГ-ММ-ДД Ч:М:С
            parsed_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        elif re.match(r'\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{1,2}:\d{1,2}', date_string):
            # Формат ДД.ММ.ГГГГ Ч:М:С
            parsed_date = datetime.strptime(date_string, "%d.%m.%Y %H:%M:%S")
        elif re.match(r'\d{2}\.\d{2}\.\d{4}', date_string):
            # Формат ДД.ММ.ГГГГ
            parsed_date = datetime.strptime(date_string, "%d.%m.%Y")
        else:
            raise ValueError(f"Неизвестный формат даты: {date_string}")

        # Возвращаем дату в формате ДД.ММ.ГГГГ
        return parsed_date.strftime("%d.%m.%Y")
    except Exception as e:
        logging.error(f"Ошибка при форматировании даты '{date_string}': {e}")
        return 'Не указано'


async def fetch_calls(session, params):
    """Асинхронный запрос к API для получения звонков."""
    headers = {"X-API-KEY": API_KEY}
    async with session.get(CALL_HISTORY_URL, params=params, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            logging.error(f"Ошибка при запросе звонков: {response.status}")
            return []


async def process_calls(project_ids):
    """Обработка входящих звонков."""
    last_call_id = int(read_last_call_id() or -1)
    params = {
        "begin_date": '01.12.2024',
        "end_date": get_today_date(),
        "user_ids[]": [
            12327, 12477, 12622, 12330, 12532, 12511, 12408, 12331, 12616, 12614, 12333, 12640, 12615, 12561, 12643,
            12610, 12594, 12357, 12595, 12575, 12656, 12461, 12462, 12463
        ]
    }

    async with aiohttp.ClientSession() as session:
        calls = await fetch_calls(session, params)

    new_last_call_id = last_call_id
    for call in calls:
        call_id = int(call.get('id', -1))
        if call_id <= last_call_id:
            continue

        # call.get('contact_status_name') == 'Горячий лид' and
        if call.get('project_id') in project_ids:
            # Форматируем даты
            date_call = await format_date(call.get('created_at', 'Не указано'))
            date_load_base = await format_date(call.get('contact_address', 'Не указано'))


            logging.info(f"Дата загрузки базы: {date_load_base}")



            # Формируем данные для добавления в базу данных
            call_data = {
                'date_load_base': date_load_base,
                'date_call': date_call,
                'project_id': call.get('project_id', 'Не указан'),
                'project_name': call.get('project_name', 'Не указано'),
                'contact_base_id': call.get('contact_base_id', 'Не указан'),
                'contact_name': call.get('contact_name', 'Не указано'),
                'contact_description': call.get('contact_description', 'Не указано'),
                'contact_id': call.get('contact_id', 'Не указан'),
                'id_call': call.get('id', 'Не указан'),
                'call_result_id': call.get('call_result_id', 'Не указан'),
                'contact_status_name': call.get('contact_status_name', 'Не указан'),
                'called_phone': format_phone_number(call.get('called_phone', 'Не указан')),
                'name_respond': extract_custom_field(call, 'Имя'),
                'remark': call.get('remark', 'Не указано'),
                'user_id': call.get('user_id', 'Не указан'),
                'operator_name': call.get('operator_name', 'Не указано'),
                'is_marriage': 0
            }
            add_to_database_analytics(**call_data)
            new_last_call_id = call_id

    if new_last_call_id != last_call_id:
        write_last_call_id(new_last_call_id)


async def main():
    init_db_analytics()
    project_ids = Project_ids
    while True:
        try:
            await process_calls(project_ids)
            logging.info("Запрос завершён. Ожидание 10 минут.")
            await asyncio.sleep(600)
        except Exception as e:
            logging.error(f"Ошибка: {e}. Повтор через 1 минуту.")
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
