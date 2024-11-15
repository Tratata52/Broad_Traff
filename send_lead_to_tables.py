import logging
from datetime import datetime


def send_lead_to_table_bath(call, WORKSHEET):
    current_date = datetime.now().strftime("%d.%m.%Y")
    row = [call[9], call[12], call[11]]
    first_empty_row = len(
        WORKSHEET.get_all_values()) + 1  # Определяет последнюю строку и прибавляет 1 для пустой строки

    try:
        WORKSHEET.insert_row(row, first_empty_row)
        logging.info(f"Успешно добавлена строка: {row}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении строки в таблицу: {e} | Данные: {row}")


def send_lead_to_table_mk_group(call, WORKSHEET):
    current_date = datetime.now().strftime("%d.%m")
    current_time = datetime.now().strftime('%H:%M')

    row = [current_date, current_time, call[12], call[9], call[11]]
    first_empty_row = len(
        WORKSHEET.get_all_values()) + 1  # Определяет последнюю строку и прибавляет 1 для пустой строки

    try:
        WORKSHEET.insert_row(row, first_empty_row)
        logging.info(f"Успешно добавлена строка: {row}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении строки в таблицу: {e} | Данные: {row}")


def send_lead_table_window(call, WORKSHEET):
    current_date = datetime.now().strftime("%d.%m.%Y")
    row = [current_date, call[9], call[12], call[11]]
    first_empty_row = len(
        WORKSHEET.get_all_values()) + 1  # Определяет последнюю строку и прибавляет 1 для пустой строки

    try:
        WORKSHEET.insert_row(row, first_empty_row)
        logging.info(f"Успешно добавлена строка: {row}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении строки в таблицу: {e} | Данные: {row}")


def send_lead_table_styrofoam(call, WORKSHEET):
    current_date = datetime.now().strftime("%d.%m.%Y")
    row = [current_date, call[9], call[12], call[11]]
    first_empty_row = len(
        WORKSHEET.get_all_values()) + 1  # Определяет последнюю строку и прибавляет 1 для пустой строки
    try:
        WORKSHEET.insert_row(row, first_empty_row)
        logging.info(f"Успешно добавлена строка: {row}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении строки в таблицу: {e} | Данные: {row}")

def send_lead_table_letter(call, WORKSHEET):
    current_date = datetime.now().strftime("%d.%m.%Y")
    row = [current_date, call[9], call[12], call[11]]
    first_empty_row = len(
        WORKSHEET.get_all_values()) + 1  # Определяет последнюю строку и прибавляет 1 для пустой строки
    try:
        WORKSHEET.insert_row(row, first_empty_row)
        logging.info(f"Успешно добавлена строка: {row}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении строки в таблицу: {e} | Данные: {row}")