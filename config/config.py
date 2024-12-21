import gspread
from oauth2client.service_account import ServiceAccountCredentials

# для бота
tg_token = '7508330790:AAFPsgmc_npycJ5BrGPI77HcSTVLz87ZN5U'
tg_test_token = '5249110429:AAFhYZg7bdXyH_a6lO_qEX_1gYJ8FFjbyMI'
json_keyfile = 'logical-air-353619-553a6e6c8351.json'
access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjZkNzM4ZWI0NjFhMWQ3ZjdkY2Q4NDEyZmUxNzI2NzUyMDdmNWU2NTQ4MGU3ODZmMWQwMTEyOTA1NTRhZDUwMzJhNTk3OGU3YzVkYTNkYTk2In0.eyJhdWQiOiJjYjExNWMyYi1hNGQ0LTRhM2UtYWIxZS0xMzM4YmZiNTdiODUiLCJqdGkiOiI2ZDczOGViNDYxYTFkN2Y3ZGNkODQxMmZlMTcyNjc1MjA3ZjVlNjU0ODBlNzg2ZjFkMDExMjkwNTU0YWQ1MDMyYTU5NzhlN2M1ZGEzZGE5NiIsImlhdCI6MTcyNDE2NTQ1MiwibmJmIjoxNzI0MTY1NDUyLCJleHAiOjE3MzU2MDMyMDAsInN1YiI6IjExMzg0NzYyIiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxODk2MDg2LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiYzA5NDAxZmMtYmU3Ny00MmEyLTk1MjgtM2QzN2I2YzFhYzdhIiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.D9MTx2wjje3EoE-r0GQMlDL6VrfMfOMtnbw2SHWpWLb2xR0HNmJP-mI_he3HNrVtfMgeuIDY1-qMbluDt5Do089hm7IPjqjj6i3veQU4R7wl5zEBZ6TNW2mDVdyQStUJ5hPmM9v4p_vbb8TNPj2XH1Nv_kIZ_y4jzG33bpsPx3zs0pkCQbyDbrPl6hiOUk6p4MgMvN5khO5727KLbYlX255k3dX-iaWkgGVXXlKPe9k1FThCP8M3LR8phKp94yWfesloN_Vw8en_bgpdmaKjwWx3JCLJU3g3GX5aEWDzFUNL_xYVGBi4wzoR2yRClxV9RoRaAeqSXPVw_vIhwPdlBw'

# Параметры
API_KEY = "CrWtR636gPGkQvh4dE6Pq3fjxXWyJXaw"
BASE_URL = "https://app.obzvonilka.ru"
USERS_URL = f'{BASE_URL}/api/users'
CALL_HISTORY_URL = f"{BASE_URL}/api/report/call_history"
VOICES_URL = f"{BASE_URL}/api/report/voices"
LAST_CALL_ID_FILE = 'last_call_id_all.txt'
GROQ_API_KEY = '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'
token_bt_crm = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjRmODcwMTNlNTY0NmEzMDgyMjNlM2EzMzkyNjM3Zjk4NDNlNDQyNDNmMmFiYzI0NDcwMGQyZWI4ZWU2MTUzZmZmZDZiNzdiZTUyMzYyMzI1In0.eyJhdWQiOiJiNTU1ZGU5MS04Yjc3LTQ4ZWUtYjRkZC01MmM5NGFhMTJlY2YiLCJqdGkiOiI0Zjg3MDEzZTU2NDZhMzA4MjIzZTNhMzM5MjYzN2Y5ODQzZTQ0MjQzZjJhYmMyNDQ3MDBkMmViOGVlNjE1M2ZmZmQ2Yjc3YmU1MjM2MjMyNSIsImlhdCI6MTcyODExMDg3MCwibmJmIjoxNzI4MTEwODcwLCJleHAiOjE3NjcxMzkyMDAsInN1YiI6IjExMTM0NDk4IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxNzgwNDE0LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiNDE5MjUwYTAtMDVlOS00NWY1LWJhNGUtZWYwYjA4NDdjOTI4IiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.BELBcwM5fJ_wAAoTB8ysbJ598sXrWId5cI-q-_HxBgUcM2hhQlUDIIheXQNkQu5S3aNNdtA5rtbmG3WVqJeBk4JYzmyC7SF4QyGXNbGVmKGheeprc9-FicxlhxvLaXMQ59AwZYNyoNT7NheZykqppXTNO5aWbwQ5Osoy7v6r1uRZb8Dg8zMyJG2qSUqyhFXnQS1dtnDeBYOvQ9ojuluFWnh1DbCfpeuGSQhTKF-SqE2rma6MwfPWGAJjhpia3CI3iWsV3C3247ySYCESv6yBNdVB1HuPBFR9J3FqlcG52jXckCS5Eg42VTTb8gBO8brEc-Coap8QPM_KHSxSZDgXYg'
access_token_mk = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjZkNzM4ZWI0NjFhMWQ3ZjdkY2Q4NDEyZmUxNzI2NzUyMDdmNWU2NTQ4MGU3ODZmMWQwMTEyOTA1NTRhZDUwMzJhNTk3OGU3YzVkYTNkYTk2In0.eyJhdWQiOiJjYjExNWMyYi1hNGQ0LTRhM2UtYWIxZS0xMzM4YmZiNTdiODUiLCJqdGkiOiI2ZDczOGViNDYxYTFkN2Y3ZGNkODQxMmZlMTcyNjc1MjA3ZjVlNjU0ODBlNzg2ZjFkMDExMjkwNTU0YWQ1MDMyYTU5NzhlN2M1ZGEzZGE5NiIsImlhdCI6MTcyNDE2NTQ1MiwibmJmIjoxNzI0MTY1NDUyLCJleHAiOjE3MzU2MDMyMDAsInN1YiI6IjExMzg0NzYyIiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjMxODk2MDg2LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiYzA5NDAxZmMtYmU3Ny00MmEyLTk1MjgtM2QzN2I2YzFhYzdhIiwiYXBpX2RvbWFpbiI6ImFwaS1iLmFtb2NybS5ydSJ9.D9MTx2wjje3EoE-r0GQMlDL6VrfMfOMtnbw2SHWpWLb2xR0HNmJP-mI_he3HNrVtfMgeuIDY1-qMbluDt5Do089hm7IPjqjj6i3veQU4R7wl5zEBZ6TNW2mDVdyQStUJ5hPmM9v4p_vbb8TNPj2XH1Nv_kIZ_y4jzG33bpsPx3zs0pkCQbyDbrPl6hiOUk6p4MgMvN5khO5727KLbYlX255k3dX-iaWkgGVXXlKPe9k1FThCP8M3LR8phKp94yWfesloN_Vw8en_bgpdmaKjwWx3JCLJU3g3GX5aEWDzFUNL_xYVGBi4wzoR2yRClxV9RoRaAeqSXPVw_vIhwPdlBw'

# Константы для домена и ID воронки/статуса
DOMAIN = "infoboardtraffru.amocrm.ru"
PIPELINE_ID = "8701282"  # ID воронки
STATUS_ID = "70487718"  # ID статуса

# Файл для хранения последнего обработанного ID сделки
LAST_LEAD_ID_FILE = "last_lead_id.txt"

# БАЗЫ ДАННЫХ
# DB_FILE = 'leads.db'
DB_FILE_analytics = 'Traffic.db'
DB_FILE = 'leads.db'
DB_FILE_users = 'user_data.db'


# Подключение к Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
JSON_KEYFILE = 'logical-air-353619-553a6e6c8351.json'
JSON_KEYFILE_test = 'logical-air-353619-37e0cacf8b53_test.json'
CREDS = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYFILE, SCOPE)
CLIENT = gspread.authorize(CREDS)

headers = {
    'Authorization': f'Bearer {token_bt_crm}',
    'Content-Type': 'application/json'
}


# Проекты
Project_ids = [11962, 11766, 12112, 12206, 12205, 12257, 12258, 12264, 12265, 12282, 12296, 12340, 12347, 12344]  # Укажите нужные project_id

# ССылки и подключение к таблицам
# test table
# SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1KXfLGJmA0lfirmK7Zslcl3XM2-30k2cHzqXQ_FuswRM/edit?gid=4684822'  # бани

SPREADSHEET_URL0 = ''  # шаблон
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1-gV-0zTNFVMpYrVeZHvsLsHBAbTX5hfJZClsOhizKoI/edit?usp=sharing'  # бани
SPREADSHEET_URL2 = 'https://docs.google.com/spreadsheets/d/1nj3nz6rXhWI0QS_Qp_ujYsy8zTByb94VDDyDRkSKDv0/edit?usp=sharing'  # МК групп
SPREADSHEET_URL3 = 'https://docs.google.com/spreadsheets/d/18odSdZgRfZxDLMt4L7NrDS99XgvX1leOgu80Y4LRKbc/edit?usp=sharing'  # Окна Саратов
SPREADSHEET_URL4 = 'https://docs.google.com/spreadsheets/d/1MaAra3WOfF95Rjiqu8x859BczyMpeyoJXk8I0rP6qIQ/edit?usp=sharing'  # ПЕНОПЛАСТ
SPREADSHEET_URL5 = 'https://docs.google.com/spreadsheets/d/1BL9dx_px8Y3KTB2pTwjYnHLnVb99o73nZGBM7R79MsY/edit?usp=sharing'  # ВАША БУКВА
SPREADSHEET_URL6 = 'https://docs.google.com/spreadsheets/d/1-kzX6WocSupoveBNaXR3JlhTOV75VL-z0roWWDRD2WQ/edit?usp=sharing'  # Мебельный центр Антарес
SPREADSHEET_URL7 = 'https://docs.google.com/spreadsheets/d/1d6WXOt3gNi6xyhr6UIVADgZnA2rZYgPajo9Yi1UWip0/edit?usp=sharing'  # Лиды ВТ
SPREADSHEET_URL8 = 'https://docs.google.com/spreadsheets/d/1v9EptpmKluRNOOd12_V4LoCLEwl4RRPqdBnRnWFLyn0/edit?usp=sharing'  # Метрика окон
SPREADSHEET_URL9 = 'https://docs.google.com/spreadsheets/d/1XMyu-wPqBORTifefM1dcWjp6-2gKc1WX32u-VA-KtXA/edit?usp=sharing'  # Топ кар
SPREADSHEET_URL10 = 'https://docs.google.com/spreadsheets/d/1suCEx1uRZyZZlSjyh9pdgq9Av3mpeKKj14pCTzEVNK4/edit?usp=sharing'  # Остекление Новосиб Окна-Нова
SPREADSHEET_URL11 = 'https://docs.google.com/spreadsheets/d/1qur1xw6DQeBMsb3HiwRbnl4uMR1OQVoakCjBw_PNK1k/edit?usp=sharing'  # Аренда Спец техники ( Вышка с оператором )
SPREADSHEET_URL12 = 'https://docs.google.com/spreadsheets/d/1b8-WoSEXhjv9xk-pTewnk4vhxCaKIB85PIU1Vs7lLEg/edit?usp=sharing' # Автопогрузчики СПБ + ЛО
SPREADSHEET_URL13 = 'https://docs.google.com/spreadsheets/d/1zJk016jvnMQNaD_jZdNQtwLCMZpeH06nzG9rA5fAoZw/edit?usp=sharing' # Монтаж ИНЖ новосиб
SPREADSHEET_URL14 = 'https://docs.google.com/spreadsheets/d/17p4O5ixick4gunL_Q3GkO0ywmvfJyh8ne015my-_Gmo/edit?usp=sharing' # Киров остекление/отделка балконов


SPREADSHEET = CLIENT.open_by_url(SPREADSHEET_URL)  # бани
SPREADSHEET2 = CLIENT.open_by_url(SPREADSHEET_URL2)  # МК групп
SPREADSHEET3 = CLIENT.open_by_url(SPREADSHEET_URL3)  # Окна
SPREADSHEET4 = CLIENT.open_by_url(SPREADSHEET_URL4)  # ПЕНОПЛАСТ
SPREADSHEET5 = CLIENT.open_by_url(SPREADSHEET_URL5)  # ВАША БУКВА
SPREADSHEET6 = CLIENT.open_by_url(SPREADSHEET_URL6)  # Мебельный центр Антарес
SPREADSHEET7 = CLIENT.open_by_url(SPREADSHEET_URL7)  # Лиды ВТ
SPREADSHEET8 = CLIENT.open_by_url(SPREADSHEET_URL8)  # Метрика окон
SPREADSHEET9 = CLIENT.open_by_url(SPREADSHEET_URL9)  # Топ кар
SPREADSHEET10 = CLIENT.open_by_url(SPREADSHEET_URL10)  # Остекление Новосиб Окна-Нова
SPREADSHEET11 = CLIENT.open_by_url(SPREADSHEET_URL11)  # Аренда Спец техники ( Вышка с оператором )
SPREADSHEET12 = CLIENT.open_by_url(SPREADSHEET_URL12) # Автопогрузчики СПБ + ЛО
SPREADSHEET13 = CLIENT.open_by_url(SPREADSHEET_URL13) # Монтаж ИНЖ
SPREADSHEET14 = CLIENT.open_by_url(SPREADSHEET_URL14) # Киров остекление/отделка балконов


WORKSHEET1 = SPREADSHEET.get_worksheet(0)  # бани
WORKSHEET2 = SPREADSHEET2.get_worksheet(0)  # МК групп
WORKSHEET3 = SPREADSHEET3.get_worksheet(0)  # ОКНА
WORKSHEET4 = SPREADSHEET4.get_worksheet(0)  # ПЕНОПЛАСТ
WORKSHEET5 = SPREADSHEET5.get_worksheet(0)  # реклама ваша буква
WORKSHEET6 = SPREADSHEET6.get_worksheet(0)  # Мебельный центр Антарес
WORKSHEET7 = SPREADSHEET7.get_worksheet(0)  # Лиды ВТ
WORKSHEET8 = SPREADSHEET8.get_worksheet(0)  # Метрика окон
WORKSHEET9 = SPREADSHEET9.get_worksheet(0)  # Топ кар
WORKSHEET10 = SPREADSHEET10.get_worksheet(0) # Остекление Новосиб Окна-Нова
WORKSHEET11 = SPREADSHEET11.get_worksheet(0) # Аренда Спец техники ( Вышка с оператором )
WORKSHEET12 = SPREADSHEET12.get_worksheet(0) # Автопогрузчики СПБ + ЛО
WORKSHEET13 = SPREADSHEET13.get_worksheet(0) # Монтаж ИНЖ
WORKSHEET14 = SPREADSHEET14.get_worksheet(0) # Киров остекление/отделка балконов