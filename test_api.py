"""
Тестовый скрипт для проверки API эндпоинтов
Демонстрирует основные функции FastAPI приложения
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_api_endpoint(method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[Any, Any]:
    """
    Универсальная функция для тестирования API эндпоинтов
    
    Args:
        method: HTTP метод (GET, POST, PUT)
        endpoint: Путь к эндпоинту
        data: Данные для отправки (для POST/PUT)
        
    Returns:
        Dict с результатом запроса
    """
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data)
        else:
            return {"error": f"Неподдерживаемый метод: {method}"}
        
        return {
            "status_code": response.status_code,
            "data": response.json() if response.content else None,
            "success": response.status_code < 400
        }
        
    except requests.exceptions.ConnectionError:
        return {"error": "Не удается подключиться к серверу. Убедитесь, что сервер запущен на localhost:8000"}
    except Exception as e:
        return {"error": f"Ошибка запроса: {e}"}

def print_result(test_name: str, result: Dict[Any, Any]):
    """Красивый вывод результата теста"""
    print(f"\n{'='*50}")
    print(f"ТЕСТ: {test_name}")
    print(f"{'='*50}")
    
    if "error" in result:
        print(f"❌ ОШИБКА: {result['error']}")
        return
    
    status = "✅ УСПЕХ" if result["success"] else "❌ ОШИБКА"
    print(f"Статус: {status} ({result['status_code']})")
    
    if result["data"]:
        print("Ответ:")
        print(json.dumps(result["data"], indent=2, ensure_ascii=False))

def main():
    """Основная функция тестирования"""
    print("🚀 ЗАПУСК ТЕСТОВ API")
    print("Убедитесь, что сервер запущен: uvicorn app:app --reload")
    
    # Тест 1: Получение информации об API
    result = test_api_endpoint("GET", "/")
    print_result("Получение информации об API", result)
    
    # Тест 2: Получение всех пользователей (может быть пустой список)
    result = test_api_endpoint("GET", "/users")
    print_result("Получение всех пользователей", result)
    
    # Тест 3: Создание пользователя
    user_data = {
        "sub_id": 987654321,
        "email": "testuser@example.com"
    }
    result = test_api_endpoint("POST", "/users/123456789", user_data)
    print_result("Создание пользователя", result)
    
    # Тест 4: Получение созданного пользователя
    result = test_api_endpoint("GET", "/users/123456789")
    print_result("Получение пользователя по ID", result)
    
    # Тест 5: Добавление суб-аккаунта
    sub_data = {
        "new_sub_id": 444555666
    }
    result = test_api_endpoint("PUT", "/users/123456789/sub-accounts", sub_data)
    print_result("Добавление суб-аккаунта", result)
    
    # Тест 6: Обновление email
    email_data = {
        "email": "newemail@example.com"
    }
    result = test_api_endpoint("PUT", "/users/123456789/email", email_data)
    print_result("Обновление email", result)
    
    # Тест 7: Получение обновленного пользователя
    result = test_api_endpoint("GET", "/users/123456789")
    print_result("Получение обновленного пользователя", result)
    
    # Тест 8: Создание второго пользователя
    user_data2 = {
        "sub_id": 111222333,
        "email": "user2@example.com"
    }
    result = test_api_endpoint("POST", "/users/987654321", user_data2)
    print_result("Создание второго пользователя", result)
    
    # Тест 9: Получение всех пользователей
    result = test_api_endpoint("GET", "/users")
    print_result("Получение всех пользователей (после создания)", result)
    
    # Тест 10: Попытка создать пользователя с существующим ID
    user_data3 = {
        "sub_id": 999888777,
        "email": "duplicate@example.com"
    }
    result = test_api_endpoint("POST", "/users/123456789", user_data3)
    print_result("Попытка создать дубликат пользователя", result)
    
    # Тест 11: Получение несуществующего пользователя
    result = test_api_endpoint("GET", "/users/999999999")
    print_result("Получение несуществующего пользователя", result)
    
    # Тест 12: Legacy эндпоинт - получение пользователя
    result = test_api_endpoint("GET", "/user/123456789")
    print_result("Legacy получение пользователя", result)
    
    # Тест 13: Legacy эндпоинт - создание пользователя
    result = test_api_endpoint("POST", "/user-create/555666777")
    print_result("Legacy создание пользователя", result)
    
    # Тест 14: Создание карты (заглушка)
    result = test_api_endpoint("POST", "/user/123456789/cards")
    print_result("Создание карты (заглушка)", result)
    
    # Тест 15: Получение карт (заглушка)
    result = test_api_endpoint("GET", "/user/123456789/cards")
    print_result("Получение карт (заглушка)", result)
    
    print(f"\n{'='*50}")
    print("🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print(f"{'='*50}")

def test_error_scenarios():
    """Тестирование сценариев ошибок"""
    print("\n🔍 ТЕСТИРОВАНИЕ СЦЕНАРИЕВ ОШИБОК")
    
    # Тест 1: Неверный JSON
    try:
        response = requests.post(
            f"{BASE_URL}/users/888999000",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        print(f"\nНеверный JSON: {response.status_code}")
    except Exception as e:
        print(f"\nНеверный JSON: {e}")
    
    # Тест 2: Отсутствующие поля
    incomplete_data = {"sub_id": 123456789}  # Отсутствует email (но это нормально)
    result = test_api_endpoint("POST", "/users/777888999", incomplete_data)
    print_result("Создание пользователя без email", result)
    
    # Тест 3: Добавление существующего суб-аккаунта
    sub_data = {"new_sub_id": 987654321}  # Уже существует
    result = test_api_endpoint("PUT", "/users/123456789/sub-accounts", sub_data)
    print_result("Добавление существующего суб-аккаунта", result)

if __name__ == "__main__":
    print("Инструкции:")
    print("1. Запустите сервер: uvicorn app:app --reload")
    print("2. Убедитесь, что база данных настроена в .env файле")
    print("3. Запустите тесты: python test_api.py")
    print("\n" + "="*60 + "\n")
    
    # Основные тесты
    main()
    
    # Тесты ошибок
    test_error_scenarios()
    
    print("\n📋 РЕЗУЛЬТАТЫ:")
    print("- Проверьте, что все тесты прошли успешно")
    print("- Ошибки 404 и 409 являются ожидаемыми для тестовых сценариев")
    print("- Убедитесь, что база данных создала таблицы и сохранила данные")
    print("\n🌐 Документация API доступна по адресу: http://localhost:8000/docs")

