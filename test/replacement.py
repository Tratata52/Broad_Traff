import gspread
from oauth2client.service_account import ServiceAccountCredentials

from ADMINKA.config.config import JSON_KEYFILE, SPREADSHEET_URL2

# Устанавливаем область доступа к API Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Авторизация с использованием ключа из JSON-файла
creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYFILE, scope)
client = gspread.authorize(creds)

# Открываем таблицу по URL
spreadsheet = client.open_by_url(SPREADSHEET_URL2)

# Открываем лист (в данном случае первый лист)
worksheet = spreadsheet.get_worksheet(1)
# Получить все строки из таблицы
all_rows = worksheet.get_all_values()

# Индекс столбца K (11-й столбец, т.к. индексация начинается с 0)
column_k_index = 10
column_j_index = 9
# Создать список для строк, где в столбце K есть слово "замена"
rows_with_replacement = []

replace_resquest = ['Дубль', 'У нас такого нет', '3 дня нет ответа', 'Заказ до 10 000 руб.']
replace_response = ['Замена лида']

# Проход по всем строкам (начиная с первой строки)
for row in all_rows:

    if len(row) > column_k_index and 'Замена лида' in row[column_k_index]:

        rows_with_replacement.append(row)

# Вывести строки, которые содержат "замена" в столбце K

for row in rows_with_replacement:
    print(row)
