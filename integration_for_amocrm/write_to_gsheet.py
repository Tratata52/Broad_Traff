import datetime
import logging


def write_to_google_sheet_stadart(sheet, name, phone, notes_text):
    current_date = datetime.now().strftime("%d.%m.%Y")  # Получение текущей даты
    row_data = [current_date, phone, name, notes_text]
    sheet.insert_row(row_data, index=len(sheet.get_all_values()) + 1)
    logging.info(f"Добавлена строка: Дата - {current_date}, Имя - {name}, Телефон - {phone}, Примечания - {notes_text}")


# Запись данных в Google Sheet бани
def write_to_google_sheet_bath(sheet, name, phone, notes_text):
    current_date = datetime.now().strftime("%d.%m.%Y")  # Получение текущей даты
    row_data = [phone, name, notes_text]
    sheet.insert_row(row_data, index=len(sheet.get_all_values()) + 1)
    logging.info(f"Добавлена строка: Дата - {current_date}, Имя - {name}, Телефон - {phone}, Примечания - {notes_text}")


# Запись данных в Google Sheet двери
def write_to_google_sheet_mk_group(sheet, name, phone, notes_text):
    current_date = datetime.now().strftime("%d.%m.%Y")
    current_time = datetime.now().strftime('%H:%M')
    # Данные для добавления
    row_data = [current_date, current_time, name, phone, None, notes_text]
    # Вставляем строку в начало (после заголовков) и всегда с колонки A
    sheet.insert_row(row_data, index=len(
        sheet.get_all_values()) + 1)  # Определяет длину текущих строк и вставляет ниже последней строки
    logging.info(f"Добавлена строка: Дата - {current_date}, Имя - {name}, Телефон - {phone}, Примечания - {notes_text}")

