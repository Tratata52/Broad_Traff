import logging
import os
import sqlite3
import time
from datetime import datetime

import librosa
import numpy as np
import requests
import soundfile as sf
from groq import Groq

# Параметры
API_KEY = "CrWtR636gPGkQvh4dE6Pq3fjxXWyJXaw"
BASE_URL = "https://app.obzvonilka.ru"
CALL_HISTORY_URL = f"{BASE_URL}/api/report/call_history"
VOICES_URL = f"{BASE_URL}/api/report/voices"
LAST_CALL_ID_FILE = 'last_call_id_all.txt'
GROQ_API_KEY = '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'
DB_FILE = 'leads.db'
DB_FILE_users = 'user_data.db'

# Инициализация Groq
GROQ_CLIENT = Groq(api_key=GROQ_API_KEY)

# Создаём папку logs, если её нет
if not os.path.exists('logs'):
    os.makedirs('logs')

# Настраиваем логирование
logging.basicConfig(filename='logs/call_processor.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


# Инициализация базы данных
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


# Сохранение данных звонка в базу данных
def add_to_database(date, user_id, manager_name, project_id, project_name, client_name, city, customer_name, phone, comment, mp3_url):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO calls (date, user_id, manager_name, project_id, project_name, client_name, city, customer_name, phone, comment, mp3_url)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (date, user_id, manager_name, project_id, project_name, client_name, city, customer_name, phone, comment, mp3_url))

    conn.commit()
    conn.close()
    logging.info(f"Добавлен звонок в БД: {customer_name}, {phone}, {manager_name}, {project_name}, mp3_url: {mp3_url}")


# Получение текущей даты
def get_today_date():
    return datetime.now().strftime("%d.%m.%Y")


# Чтение последнего ID записи
def get_last_call_id():
    if os.path.exists(LAST_CALL_ID_FILE):
        with open(LAST_CALL_ID_FILE, 'r') as file:
            return file.read().strip()
    return None


# Сохранение последнего ID записи
def save_last_call_id(call_id):
    with open(LAST_CALL_ID_FILE, 'w') as file:
        file.write(str(call_id))


# Очистка папки записей
def clear_records_folder():
    for filename in os.listdir('records'):
        file_path = os.path.join('records', filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


# Функция для получения списка user_id из базы данных
def get_user_ids():
    conn = sqlite3.connect(DB_FILE_users)
    cursor = conn.cursor()

    # Получаем все user_id из таблицы users
    cursor.execute("SELECT user_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]

    conn.close()
    return user_ids


# Запрос для получения новых звонков
def check_for_new_calls(project_ids):
    begin_date = get_today_date()  # Начальная дата
    end_date = get_today_date()  # Конечная дата
    last_call_id_str = get_last_call_id()
    last_call_id = int(last_call_id_str) if last_call_id_str is not None else -1  # Преобразование в int

    # Получаем список user_id из базы данных
    user_ids = get_user_ids()

    # Параметры запроса
    params = {
        "begin_date": begin_date,
        "end_date": end_date,
        "user_ids[]": user_ids,
    }
    headers = {"X-API-KEY": API_KEY}

    # Отправка запроса
    response = requests.get(CALL_HISTORY_URL, params=params, headers=headers)

    if response.status_code == 200:
        json_data = response.json()
        new_last_call_id = last_call_id

        for call in json_data:
            # print(call)
            call_id_str = call.get('id')
            call_id = int(call_id_str) if call_id_str is not None else -1

            if call_id <= last_call_id:
                continue  # Пропускаем обработанные звонки

            contact_status = call.get('contact_status_name')
            project_id = call.get('project_id')
            contact_id = call.get('contact_id')
            category = call.get('name')

            if contact_status == 'Горячий лид' and project_id in project_ids:
                if contact_id:
                    # Получаем записи голоса
                    if process_voice(contact_id, begin_date, end_date, call):
                        new_last_call_id = call_id

        if new_last_call_id != last_call_id:
            save_last_call_id(new_last_call_id)
        elif new_last_call_id == last_call_id:
            print("Новых записей не обнаружено")
        else:
            print(f"Ошибка при запросе списка звонков: {response.status_code}")


# СКАЧАТЬ MP3
def process_voice(contact_id, begin_date, end_date, call):
    voice_params = {
        "begin_date": begin_date,
        "end_date": end_date,
        "contact_id": contact_id
    }
    voice_response = requests.get(VOICES_URL, params=voice_params, headers={"X-API-KEY": API_KEY})

    if voice_response.status_code == 200:
        voice_data = voice_response.json()
        print(voice_data)

        if 'voices' in voice_data:
            voices = voice_data['voices']
            for voice in voices:
                call_history = voice.get('call_history', {})
                call_result = call_history.get('call_result', {})
                result_name = call_result.get('name', '')
                if result_name == 'Горячий лид':

                    mp3_url = voice.get('public_voice_url')

                    if mp3_url:
                        download_and_process_audio(mp3_url, call)
                        return mp3_url  # Обработано успешно
            else:
                print("Ключ 'voices' не найден в ответе.")
        else:
            print(f"Ошибка при запросе ссылок на записи для контакта {contact_id}: {voice_response.status_code}")

        return False  # Не удалось обработать


# Скачивание MP3
def download_and_process_audio(mp3_url, call):
    mp3_filename = f"{call['id']}.mp3"
    mp3_path = os.path.join('records', mp3_filename)

    response = requests.get(mp3_url, stream=True)
    if response.status_code == 200:
        with open(mp3_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        # print(f"Скачан файл: {mp3_path}")

        improved_audio_path = enhance_audio(mp3_path)
        process_audio(improved_audio_path, call, mp3_url)

    else:
        print(f"Ошибка при скачивании MP3: {response.status_code}")


# ОБРАБОТКА АУДИО
def enhance_audio(file_path):
    # Загружаем аудио
    y, sr = librosa.load(file_path, sr=None)

    # Нормализация громкости
    y_normalized = librosa.util.normalize(y)

    # Применение предысказания (pre-emphasis) для усиления высоких частот
    y_preemphasis = librosa.effects.preemphasis(y_normalized)

    # Удаление тишины и сокращение интервалов
    intervals = librosa.effects.split(y_preemphasis, top_db=40)  # Уменьшение уровня тишины
    y_cleaned = librosa.effects.remix(y_preemphasis, intervals=intervals)

    # Применение метода сглаживания
    y_smoothed = librosa.effects.preemphasis(y_cleaned, coef=3.0)  # Регулировка коэффициента предысказания
    y_louder = np.clip(y_smoothed, -1.0, 1.0)  # Ограничение значений для предотвращения искажения

    # Преобразование в WAV и сохранение
    improved_file_path = file_path.replace('.mp3', '_enhanced.wav')
    sf.write(improved_file_path, y_louder, sr)

    return improved_file_path


# llama3-70b-8192-tool-use-preview
def get_chat_response(user_input, temp, max_tokens):
    chat_completion = GROQ_CLIENT.chat.completions.create(
        messages=[{"role": "system",
                   "content": f'{user_input}.Что нужно клиенту? Укажи что клиент ждет информации на вацап'}],
        model="llama3-groq-70b-8192-tool-use-preview",  # ЯЗЫКОВАЯ МОДЕЛЬ
        temperature=temp,  # ТЕМПЕРАТУРА
        max_tokens=max_tokens,  # КОЛ-ВО СЛОВ
        top_p=0.1,
    )
    return chat_completion.choices[0].message.content


# Транскрипция аудио
def transcribe_audio_with_whisper(file_path):
    with open(file_path, 'rb') as file:
        # Отправляем запрос на транскрипцию аудио
        transcription = GROQ_CLIENT.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3-turbo",
            language="ru",
            response_format="verbose_json",
            temperature=0.38,
        )

        # Предположим, что segments - это атрибут объекта transcription
        segments = transcription.segments if hasattr(transcription, 'segments') else []
        formatted_text = ""
        for segment in segments:
            start_time = segment["start"]
            end_time = segment["end"]
            text = segment["text"]
            formatted_text += f"[{start_time:.2f} - {end_time:.2f}] {text}\n"

        return formatted_text.strip()


def extract_name_and_city(call):
    # Извлечение имени и города из custom_fields
    name = None
    city = None

    for field in call.get('custom_fields', []):
        if field.get('title') == 'Имя':
            name = field.get('value')
        elif field.get('title') == 'Город':
            city = field.get('value')

    return name, city

# Обработка текста
def process_audio(file_path, call, mp3_url):
    text = transcribe_audio_with_whisper(file_path)
    user_id = call.get('user_id', 'Не указан')
    phone = call.get('called_phone', 'Не указан')
    manager_name = call.get('operator_name', 'Не указан')
    customer_name = call.get('remark', 'Не указано')
    project_name = call.get('project_name', 'Не указан')
    project_id = call.get('project_id', 'Не указан')
    # Извлекаем имя и город
    client_name, city = extract_name_and_city(call)


#     roles_prompt = f"""Распределите роли в следующем разговоре между оператором компании и клиентом:
# Оператор:
# Приветствует клиента и задает вопросы про покупку.
# Уточняет информацию прямыми, закрытыми или альтернативными вопросами.
# Часто спрашивает: "Как могу к вам обращаться?".
# Завершает разговор прощанием.
#
# Клиент:
# Отвечает на вопросы оператора, уточняет детали, выражает интерес или отказывается.
# Может упоминать, что общается от лица другого человека.
# Также может попрощаться в конце разговора.
#
# Инструкции:
# Реплики оператора начинаются с приветствия и вопроса.
# Реплики клиента — ответы на вопросы или комментарии.
# Реплики должны быть помечены "Оператор:" или "Клиент:".
# Диалог должен быть последовательным и логичным.
# Избегайте повторений фраз.
# Работайте только с входным текстом, не добавляйте ничего нового.
#
# Текст:
# {text}
# """

    # roles_text = get_chat_response(roles_prompt, 0.8, 1024)

    comment_prompt = f"""Расскажите подробно, учитывая размеры и цвет,количество и другие детали, что хочет клиент.
Не упоминайте имён людей, названия компаний и бренды. Начинайте рассказ со слова "Интересуется ..." 
Текст:
{text}   
"""

    comment = get_chat_response(comment_prompt, 1, 512)

    # Сохраняем данные в базу
    add_to_database(get_today_date(), user_id, manager_name, project_id, project_name, client_name, city, customer_name, phone, comment, mp3_url)



# Основная функция
def main():
    init_db()

    while True:
        clear_records_folder()
        project_ids = [11962, 11766,12112]  # Укажите нужные project_id
        check_for_new_calls(project_ids)
        print('Повторный запрос через 2 минуты')
        time.sleep(120)  # Задержка между проверками


if __name__ == "__main__":
    main()
