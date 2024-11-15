import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Параметры
API_KEY = "CrWtR636gPGkQvh4dE6Pq3fjxXWyJXaw"
BASE_URL = "https://app.obzvonilka.ru"
CALL_HISTORY_URL = f"{BASE_URL}/api/report/call_history"
VOICES_URL = f"{BASE_URL}/api/report/voices"
LAST_CALL_ID_FILE = 'last_call_id_all.txt'
GROQ_API_KEY = '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'
token_bt_crm = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjRmODcwMTNlNTY0NmEzMDgyMjNlM2EzMzkyNjM3Zjk4NDNlNDQyNDNmMmFiYzI0NDcwMGQyZWI4ZWU2MTUzZmZmZDZiNzdiZTUyMzYyMzI1In0.eyJhdWQiOiJiNTU1ZGU5MS04Yjc3LTQ4ZWUtYjRkZC01MmM5NGFhMTJlY2YiLCJqdGkiOiI0Zjg3MDEzZTU2NDZhMzA4MjIzZTNhMzM5MjYzN2Y5ODQzZTQ0MjQzZjJhYmMyNDQ3MDBkMmViOGVlNjE1M2ZmZmQ2Yjc3YmU1MjM2MjMyNSIsImlhdCI6MTcyODExMDg3MCwibmJmIjoxNzI4MTEwODcwLCJleHAiOjE3NjcxMzkyMDAsInN1YiI6IjExMTM0NDk4IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNzgwNDE0LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiNDE5MjUwYTAtMDVlOS00NWY1LWJhNGUtZWYwYjA4NDdjOTI4IiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.BELBcwM5fJ_wAAoTB8ysbJ598sXrWId5cI-q-_HxBgUcM2hhQlUDIIheXQNkQu5S3aNNdtA5rtbmG3WVqJeBk4JYzmyC7SF4QyGXNbGVmKGheeprc9-FicxlhxvLaXMQ59AwZYNyoNT7NheZykqppXTNO5aWbwQ5Osoy7v6r1uRZb8Dg8zMyJG2qSUqyhFXnQS1dtnDeBYOvQ9ojuluFWnh1DbCfpeuGSQhTKF-SqE2rma6MwfPWGAJjhpia3CI3iWsV3C3247ySYCESv6yBNdVB1HuPBFR9J3FqlcG52jXckCS5Eg42VTTb8gBO8brEc-Coap8QPM_KHSxSZDgXYg'

# Константы для домена и ID воронки/статуса
DOMAIN = "infoboardtraffru.amocrm.ru"
PIPELINE_ID = "8701282"  # ID воронки
STATUS_ID = "70487718"  # ID статуса

# Файл для хранения последнего обработанного ID сделки
LAST_LEAD_ID_FILE = "last_lead_id.txt"

# БАЗЫ ДАННЫХ
DB_FILE = 'leads.db'
DB_FILE_users = 'user_data.db'

# Подключение к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
JSON_KEYFILE = 'logical-air-353619-d959f6958ff1.json'
CREDS = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYFILE, SCOPE)
CLIENT = gspread.authorize(CREDS)

# test table
# SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1KXfLGJmA0lfirmK7Zslcl3XM2-30k2cHzqXQ_FuswRM/edit?gid=4684822'  # бани


SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1-gV-0zTNFVMpYrVeZHvsLsHBAbTX5hfJZClsOhizKoI/edit?gid=1129040397#gid=1129040397'  # бани
SPREADSHEET_URL2 = 'https://docs.google.com/spreadsheets/d/1nj3nz6rXhWI0QS_Qp_ujYsy8zTByb94VDDyDRkSKDv0/edit?gid=2050218078#gid=2050218078'  # МК групп
SPREADSHEET_URL3 = 'https://docs.google.com/spreadsheets/d/18odSdZgRfZxDLMt4L7NrDS99XgvX1leOgu80Y4LRKbc/edit?gid=815630126#gid=815630126'  # Окна
SPREADSHEET_URL4 = 'https://docs.google.com/spreadsheets/d/1MaAra3WOfF95Rjiqu8x859BczyMpeyoJXk8I0rP6qIQ/edit?gid=1151820363#gid=1151820363'  # ПЕНОПЛАСТ
SPREADSHEET_URL5 = 'https://docs.google.com/spreadsheets/d/1BL9dx_px8Y3KTB2pTwjYnHLnVb99o73nZGBM7R79MsY/edit?gid=1290392330#gid=1290392330'  # ВАША БУКВА

SPREADSHEET = CLIENT.open_by_url(SPREADSHEET_URL)
SPREADSHEET2 = CLIENT.open_by_url(SPREADSHEET_URL2)
SPREADSHEET3 = CLIENT.open_by_url(SPREADSHEET_URL3)
SPREADSHEET4 = CLIENT.open_by_url(SPREADSHEET_URL4)
SPREADSHEET5 = CLIENT.open_by_url(SPREADSHEET_URL5)

WORKSHEET1 = SPREADSHEET.get_worksheet(0)  # бани
WORKSHEET2 = SPREADSHEET2.get_worksheet(0)  # МК групп
WORKSHEET3 = SPREADSHEET3.get_worksheet(0)  # ОКНА
WORKSHEET4 = SPREADSHEET4.get_worksheet(0)  # ПЕНОПЛАСТ
WORKSHEET5 = SPREADSHEET5.get_worksheet(0)  # реклама буква ю

headers = {
    'Authorization': f'Bearer {token_bt_crm}',
    'Content-Type': 'application/json'
}
