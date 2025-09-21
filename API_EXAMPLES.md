# Примеры использования API

Документация с примерами запросов к FastAPI приложению для управления пользователями.

## Запуск сервера

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

После запуска документация API будет доступна по адресу: http://localhost:8000/docs

## Основные эндпоинты

### 1. Получение информации об API

**GET** `/`

```bash
curl -X GET "http://localhost:8000/"
```

**Ответ:**
```json
{
  "message": "User Management API",
  "version": "1.0.0",
  "endpoints": {
    "GET /users": "Получить всех пользователей",
    "GET /users/{user_id}": "Получить пользователя по ID",
    "POST /users": "Создать нового пользователя",
    "PUT /users/{user_id}/sub-accounts": "Добавить суб-аккаунт",
    "PUT /users/{user_id}/email": "Обновить email пользователя"
  }
}
```

### 2. Получение всех пользователей

**GET** `/users`

```bash
curl -X GET "http://localhost:8000/users"
```

**Ответ:**
```json
[
  {
    "id": 123456789,
    "sub_ids": [987654321, 444555666, 777888999],
    "email": "user1@example.com",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T11:45:00"
  },
  {
    "id": 987654321,
    "sub_ids": [123456789, 333444555],
    "email": "user2@example.com",
    "created_at": "2024-01-15T10:35:00",
    "updated_at": "2024-01-15T12:00:00"
  }
]
```

### 3. Получение пользователя по ID

**GET** `/users/{user_id}`

```bash
curl -X GET "http://localhost:8000/users/123456789"
```

**Ответ:**
```json
{
  "id": 123456789,
  "sub_ids": [987654321, 444555666, 777888999],
  "email": "user1@example.com",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T11:45:00"
}
```

**Ошибка 404 (пользователь не найден):**
```json
{
  "detail": "Пользователь с ID 999999999 не найден"
}
```

### 4. Создание нового пользователя

**POST** `/users/{user_id}`

```bash
curl -X POST "http://localhost:8000/users/555666777" \
  -H "Content-Type: application/json" \
  -d '{
    "sub_id": 111222333,
    "email": "newuser@example.com"
  }'
```

**Ответ:**
```json
{
  "success": true,
  "message": "Пользователь 555666777 создан успешно"
}
```

**Создание пользователя без email:**
```bash
curl -X POST "http://localhost:8000/users/777888999" \
  -H "Content-Type: application/json" \
  -d '{
    "sub_id": 222333444
  }'
```

**Ошибка 409 (пользователь уже существует):**
```json
{
  "detail": "Пользователь с ID 123456789 уже существует"
}
```

### 5. Добавление суб-аккаунта

**PUT** `/users/{user_id}/sub-accounts`

```bash
curl -X PUT "http://localhost:8000/users/123456789/sub-accounts" \
  -H "Content-Type: application/json" \
  -d '{
    "new_sub_id": 999888777
  }'
```

**Ответ:**
```json
{
  "success": true,
  "message": "Суб-аккаунт 999888777 добавлен пользователю 123456789"
}
```

**Ошибка 404 (пользователь не найден):**
```json
{
  "detail": "Пользователь с ID 999999999 не найден"
}
```

**Ошибка 409 (суб-аккаунт уже существует):**
```json
{
  "detail": "Суб-аккаунт 987654321 уже существует у пользователя 123456789"
}
```

### 6. Обновление email пользователя

**PUT** `/users/{user_id}/email`

```bash
curl -X PUT "http://localhost:8000/users/123456789/email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com"
  }'
```

**Ответ:**
```json
{
  "success": true,
  "message": "Email пользователя 123456789 обновлен успешно"
}
```

**Ошибка 404 (пользователь не найден):**
```json
{
  "detail": "Пользователь с ID 999999999 не найден"
}
```

## Legacy эндпоинты (для совместимости)

### 7. Legacy получение пользователя

**GET** `/user/{user_id}`

```bash
curl -X GET "http://localhost:8000/user/123456789"
```

**Ответ:**
```json
{
  "id": 123456789,
  "Sub-IDs": [987654321, 444555666, 777888999],
  "Email": "user1@example.com",
  "Создан": "2024-01-15T10:30:00",
  "Обновлен": "2024-01-15T11:45:00"
}
```

### 8. Legacy создание пользователя

**POST** `/user-create/{user_id}`

```bash
curl -X POST "http://localhost:8000/user-create/888999000"
```

**Ответ:**
```json
{
  "success": true,
  "message": "Пользователь 888999000 создан успешно"
}
```

### 9. Создание карты (заглушка)

**POST** `/user/{user_id}/cards`

```bash
curl -X POST "http://localhost:8000/user/123456789/cards"
```

**Ответ:**
```json
{
  "user_id": 123456789,
  "message": "card created"
}
```

### 10. Получение карт пользователя (заглушка)

**GET** `/user/{user_id}/cards`

```bash
curl -X GET "http://localhost:8000/user/123456789/cards"
```

**Ответ:**
```json
{
  "user_id": 123456789,
  "cards": []
}
```

## Примеры с Python requests

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Создание пользователя
def create_user(user_id, sub_id, email=None):
    data = {"sub_id": sub_id}
    if email:
        data["email"] = email
    
    response = requests.post(
        f"{BASE_URL}/users/{user_id}",
        json=data
    )
    return response.json()

# Получение пользователя
def get_user(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    return response.json()

# Добавление суб-аккаунта
def add_sub_account(user_id, new_sub_id):
    data = {"new_sub_id": new_sub_id}
    response = requests.put(
        f"{BASE_URL}/users/{user_id}/sub-accounts",
        json=data
    )
    return response.json()

# Обновление email
def update_email(user_id, email):
    data = {"email": email}
    response = requests.put(
        f"{BASE_URL}/users/{user_id}/email",
        json=data
    )
    return response.json()

# Пример использования
if __name__ == "__main__":
    # Создание пользователя
    result = create_user(123456789, 987654321, "user@example.com")
    print("Создание пользователя:", result)
    
    # Получение пользователя
    user = get_user(123456789)
    print("Данные пользователя:", user)
    
    # Добавление суб-аккаунта
    result = add_sub_account(123456789, 444555666)
    print("Добавление суб-аккаунта:", result)
    
    # Обновление email
    result = update_email(123456789, "newemail@example.com")
    print("Обновление email:", result)
```

## Коды ошибок

- **200** - Успешный запрос
- **400** - Неверные параметры запроса
- **404** - Ресурс не найден (пользователь не существует)
- **409** - Конфликт (пользователь уже существует, суб-аккаунт уже существует)
- **500** - Внутренняя ошибка сервера

## Автоматическая документация

FastAPI автоматически генерирует интерактивную документацию:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Логирование

Все операции логируются с уровнем INFO. Логи включают:
- Успешные операции
- Ошибки
- Время выполнения запросов
- Детали ошибок базы данных


