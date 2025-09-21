"""
Пример использования модуля db.py
Демонстрирует основные функции для работы с базой данных пользователей
"""

import asyncio
import os
from db import (
    connect_db, 
    disconnect_db, 
    create_user, 
    update_user_add_sub, 
    update_user_email,
    get_user, 
    get_all_users
)

async def main():
    """Основная функция с примерами использования"""
    
    print("=== Демонстрация работы с базой данных ===\n")
    
    try:
        # Подключение к базе данных
        print("1. Подключение к базе данных...")
        await connect_db()
        print("   ✓ Подключение успешно\n")
        
        # Создание пользователей
        print("2. Создание пользователей:")
        
        # Пользователь 1
        success = await create_user(123456789, 987654321, "user1@example.com")
        print(f"   Пользователь 1: {success}")
        
        # Пользователь 2
        success = await create_user(987654321, 123456789, "user2@example.com")
        print(f"   Пользователь 2: {success}")
        
        # Пользователь 3 без email
        success = await create_user(555666777, 111222333)
        print(f"   Пользователь 3 (без email): {success}")
        
        print()
        
        # Добавление суб-аккаунтов
        print("3. Добавление суб-аккаунтов:")
        
        success = await update_user_add_sub(123456789, 444555666)
        print(f"   Суб-аккаунт 444555666 пользователю 123456789: {success}")
        
        success = await update_user_add_sub(123456789, 777888999)
        print(f"   Суб-аккаунт 777888999 пользователю 123456789: {success}")
        
        success = await update_user_add_sub(987654321, 333444555)
        print(f"   Суб-аккаунт 333444555 пользователю 987654321: {success}")
        
        print()
        
        # Обновление email
        print("4. Обновление email:")
        
        success = await update_user_email(555666777, "user3@example.com")
        print(f"   Email пользователя 555666777: {success}")
        
        success = await update_user_email(123456789, "newemail1@example.com")
        print(f"   Новый email пользователя 123456789: {success}")
        
        print()
        
        # Получение данных пользователей
        print("5. Получение данных пользователей:")
        
        user1 = await get_user(123456789)
        if user1:
            print(f"   Пользователь 123456789:")
            print(f"     ID: {user1['id']}")
            print(f"     Email: {user1['email']}")
            print(f"     Sub-IDs: {user1['sub_ids']}")
            print(f"     Создан: {user1['created_at']}")
        
        user2 = await get_user(987654321)
        if user2:
            print(f"   Пользователь 987654321:")
            print(f"     ID: {user2['id']}")
            print(f"     Email: {user2['email']}")
            print(f"     Sub-IDs: {user2['sub_ids']}")
        
        print()
        
        # Получение всех пользователей
        print("6. Все пользователи в системе:")
        all_users = await get_all_users()
        
        for i, user in enumerate(all_users, 1):
            print(f"   {i}. ID: {user['id']}")
            print(f"      Email: {user['email']}")
            print(f"      Sub-IDs: {user['sub_ids']}")
            print(f"      Создан: {user['created_at']}")
            print()
        
        print(f"Всего пользователей: {len(all_users)}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        
    finally:
        # Отключение от базы данных
        print("\n7. Отключение от базы данных...")
        await disconnect_db()
        print("   ✓ Отключение успешно")


async def test_error_handling():
    """Тестирование обработки ошибок"""
    print("\n=== Тестирование обработки ошибок ===\n")
    
    try:
        await connect_db()
        
        # Попытка создать пользователя без подключения к БД
        print("1. Попытка создать пользователя с существующим ID:")
        success = await create_user(123456789, 999888777, "duplicate@example.com")
        print(f"   Результат: {success}")
        
        # Попытка добавить суб-аккаунт несуществующему пользователю
        print("\n2. Попытка добавить суб-аккаунт несуществующему пользователю:")
        success = await update_user_add_sub(999999999, 111222333)
        print(f"   Результат: {success}")
        
        # Попытка обновить email несуществующему пользователю
        print("\n3. Попытка обновить email несуществующему пользователю:")
        success = await update_user_email(999999999, "nonexistent@example.com")
        print(f"   Результат: {success}")
        
        # Получение несуществующего пользователя
        print("\n4. Получение несуществующего пользователя:")
        user = await get_user(999999999)
        print(f"   Результат: {user}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await disconnect_db()


if __name__ == "__main__":
    print("Инструкции по настройке:")
    print("1. Создайте файл .env в корне проекта")
    print("2. Добавьте переменные для подключения к PostgreSQL:")
    print("   DATABASE_URL=postgresql://username:password@localhost:5432/database_name")
    print("   или")
    print("   DATABASE_USERNAME=username")
    print("   DATABASE_PASSWORD=password")
    print("   DATABASE_HOST=localhost")
    print("   DATABASE_PORT=5432")
    print("   DATABASE_NAME=database_name")
    print("3. Убедитесь, что PostgreSQL запущен и доступен")
    print("4. Запустите: python db_example.py")
    print("\n" + "="*50 + "\n")
    
    # Запуск основных примеров
    asyncio.run(main())
    
    # Запуск тестов обработки ошибок
    asyncio.run(test_error_handling())

