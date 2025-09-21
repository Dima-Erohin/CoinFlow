# Модуль базы данных (db.py)

Асинхронный модуль для работы с PostgreSQL базой данных через asyncpg. Включает функции для управления пользователями и их суб-аккаунтами.

## Возможности

- ✅ Асинхронное подключение к PostgreSQL через asyncpg
- ✅ Автоматическое создание таблиц и индексов
- ✅ Управление пользователями с суб-аккаунтами
- ✅ Поддержка PostgreSQL массивов для sub_ids
- ✅ Автоматическое обновление timestamps
- ✅ Полное логирование операций
- ✅ Обработка ошибок

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` в корне проекта:
```env
# Вариант 1: Полный URL подключения
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Вариант 2: Отдельные параметры
DATABASE_USERNAME=username
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=database_name
```

## Структура таблицы users

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY,           -- ID пользователя из Telegram
    sub_ids BIGINT[] DEFAULT '{}',   -- Массив ID суб-аккаунтов
    email TEXT,                      -- Email пользователя (может быть NULL)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Основные функции

### connect_db() -> asyncpg.Pool
Создание подключения к базе данных PostgreSQL.

**Возвращает:**
- `asyncpg.Pool`: Пул соединений с базой данных

**Исключения:**
- `ValueError`: Если не найдены необходимые переменные окружения
- `asyncpg.PostgresError`: При ошибке подключения к БД

### disconnect_db()
Закрытие подключения к базе данных.

### create_user(id: int, sub_id: int, email: Optional[str] = None) -> bool
Создание нового пользователя.

**Параметры:**
- `id` (int): ID пользователя из Telegram (bigint)
- `sub_id` (int): ID суб-аккаунта (bigint)
- `email` (Optional[str]): Email пользователя (может быть None)

**Возвращает:**
- `bool`: True если пользователь создан успешно, False если уже существует

### update_user_add_sub(id: int, new_sub_id: int) -> bool
Добавление нового суб-аккаунта пользователю.

**Параметры:**
- `id` (int): ID пользователя
- `new_sub_id` (int): ID нового суб-аккаунта

**Возвращает:**
- `bool`: True если суб-аккаунт добавлен успешно, False если пользователь не найден

### update_user_email(id: int, email: str) -> bool
Обновление или установка email пользователя.

**Параметры:**
- `id` (int): ID пользователя
- `email` (str): Новый email

**Возвращает:**
- `bool`: True если email обновлен успешно, False если пользователь не найден

### get_user(id: int) -> Optional[Dict[str, Any]]
Получение данных пользователя.

**Параметры:**
- `id` (int): ID пользователя

**Возвращает:**
- `Dict` с данными пользователя или `None` если не найден

**Структура возвращаемого словаря:**
```python
{
    'id': int,
    'sub_ids': List[int],
    'email': Optional[str],
    'created_at': datetime,
    'updated_at': datetime
}
```

### get_all_users() -> List[Dict[str, Any]]
Получение списка всех пользователей.

**Возвращает:**
- `List[Dict]`: Список всех пользователей, отсортированный по дате создания

## Примеры использования

### Базовое использование
```python
import asyncio
from db import connect_db, disconnect_db, create_user, get_user

async def main():
    # Подключение к базе данных
    await connect_db()
    
    try:
        # Создание пользователя
        success = await create_user(
            id=123456789,
            sub_id=987654321,
            email="user@example.com"
        )
        print(f"Пользователь создан: {success}")
        
        # Получение данных пользователя
        user = await get_user(123456789)
        print(f"Данные пользователя: {user}")
        
    finally:
        # Отключение от базы данных
        await disconnect_db()

# Запуск
asyncio.run(main())
```

### Работа с суб-аккаунтами
```python
from db import update_user_add_sub, get_user

async def add_sub_account():
    await connect_db()
    
    try:
        # Добавление суб-аккаунта
        success = await update_user_add_sub(123456789, 111222333)
        print(f"Суб-аккаунт добавлен: {success}")
        
        # Проверка результата
        user = await get_user(123456789)
        print(f"Суб-аккаунты: {user['sub_ids']}")
        
    finally:
        await disconnect_db()
```

### Обновление email
```python
from db import update_user_email

async def update_email():
    await connect_db()
    
    try:
        # Обновление email
        success = await update_user_email(123456789, "newemail@example.com")
        print(f"Email обновлен: {success}")
        
    finally:
        await disconnect_db()
```

### Получение всех пользователей
```python
from db import get_all_users

async def list_all_users():
    await connect_db()
    
    try:
        # Получение всех пользователей
        users = await get_all_users()
        
        for user in users:
            print(f"ID: {user['id']}, Email: {user['email']}, Sub-IDs: {user['sub_ids']}")
        
    finally:
        await disconnect_db()
```

## Обработка ошибок

Модуль включает обработку следующих ошибок:
- Отсутствие подключения к базе данных
- Дублирование пользователей
- Несуществующие пользователи
- Ошибки PostgreSQL
- Проблемы с сетью

## Логирование

Все операции логируются с использованием стандартного модуля `logging`:
- INFO: Успешные операции
- WARNING: Предупреждения (дублирование, несуществующие пользователи)
- ERROR: Ошибки выполнения

## Автоматические функции

### Триггеры
- Автоматическое обновление `updated_at` при изменении записи

### Индексы
- Индекс по email для быстрого поиска

## Безопасность

- Использование параметризованных запросов для предотвращения SQL-инъекций
- Валидация входных данных
- Безопасное управление соединениями через пул

## Производительность

- Пул соединений (1-10 соединений)
- Таймаут команд: 60 секунд
- Индексы для быстрого поиска
- Эффективные SQL-запросы

## Запуск примера

```bash
python db.py
```

## Интеграция с другими модулями

Модуль `db.py` может быть интегрирован с:
- Telegram ботом (aiogram)
- FastAPI приложением
- Модулем платежей (`payments.py`)

Пример интеграции с FastAPI:
```python
from fastapi import FastAPI
from db import connect_db, disconnect_db, get_user

app = FastAPI()

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

@app.get("/users/{user_id}")
async def get_user_endpoint(user_id: int):
    return await get_user(user_id)
```

