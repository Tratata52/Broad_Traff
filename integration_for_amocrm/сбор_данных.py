import requests
from approw_leads_for_crm import token_bt_crm as tk

# Заголовки для запросов
headers = {
    'Authorization': f'Bearer {tk}',
    'Content-Type': 'application/json'
}

# Универсальная функция для API-запросов
def api_request(endpoint):
    """
    Универсальная функция для выполнения GET-запросов к API.
    Args:
        endpoint (str): URL конечной точки API.
    Returns:
        dict: Ответ в формате JSON, если запрос успешен, иначе None.
    """
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()  # Возвращаем данные в формате JSON
    else:
        print(f"Ошибка при запросе {endpoint}: {response.status_code}")
        print(response.json())
        return None

# Функции для получения данных из разных частей API
def get_leads():
    return api_request("https://infoboardtraffru.amocrm.ru/api/v4/leads")

def get_contacts():
    return api_request("https://infoboardtraffru.amocrm.ru/api/v4/contacts")

def get_companies():
    return api_request("https://infoboardtraffru.amocrm.ru/api/v4/companies")

def get_tasks():
    return api_request("https://infoboardtraffru.amocrm.ru/api/v4/tasks")

def get_users():
    return api_request("https://infoboardtraffru.amocrm.ru/api/v4/users")

def get_pipelines():
    return api_request("https://infoboardtraffru.amocrm.ru/api/v4/leads/pipelines")

def get_custom_fields():
    return api_request("https://infoboardtraffru.amocrm.ru/api/v4/leads/custom_fields")

# Новые функции для получения пользователей и пользовательских полей
def get_users_infoboardtraffru():
    """
    Получение списка пользователей с домена infoboardtraffru.
    """
    return api_request("https://infoboardtraffru.amocrm.ru/api/v4/users")

def get_custom_fields_infoboardtraffru():
    """
    Получение списка пользовательских полей для контактов с домена infoboardtraffru.
    """
    return api_request("https://infoboardtraffru.amocrm.ru/api/v4/contacts/custom_fields")

# Основная логика программы
def main():
    # Получаем информацию о пользователях
    users_data = get_users()
    if users_data:
        print("Информация о пользователях:")
        for user in users_data['_embedded']['users']:
            print(f"ID: {user['id']}, Имя: {user['name']}")

    # Получаем информацию о пользовательских полях
    fields_data = get_custom_fields()
    if fields_data:
        print("\nИнформация о полях:")
        for field in fields_data['_embedded']['custom_fields']:
            print(f"ID: {field['id']}, Название: {field['name']}")

    # Получаем информацию о воронках
    pipelines_data = get_pipelines()
    if pipelines_data:
        print("\nИнформация о воронках:")
        for pipeline in pipelines_data['_embedded']['pipelines']:
            print(f"ID: {pipeline['id']}, Название: {pipeline['name']}")

    # Получаем информацию о пользователях с infoboardtraffru
    users_infoboardtraffru = get_users_infoboardtraffru()
    if users_infoboardtraffru:
        print("\nИнформация о пользователях с infoboardtraffru:")
        for user in users_infoboardtraffru['_embedded']['users']:
            print(f"ID: {user['id']}, Имя: {user['name']}")

    # Получаем информацию о пользовательских полях с infoboardtraffru
    custom_fields_infoboardtraffru = get_custom_fields_infoboardtraffru()
    if custom_fields_infoboardtraffru:
        print("\nИнформация о пользовательских полях с infoboardtraffru:")
        for field in custom_fields_infoboardtraffru['_embedded']['custom_fields']:
            print(f"ID: {field['id']}, Название: {field['name']}")

if __name__ == "__main__":
    main()
