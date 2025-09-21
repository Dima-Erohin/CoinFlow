"""
Модуль для работы с PostgreSQL базой данных через asyncpg.
Включает функции для управления пользователями и их суб-аккаунтами.
"""

import asyncpg
import os
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация базы данных
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "CoinFlow")

# Глобальная переменная для пула соединений
pool: Optional[asyncpg.Pool] = None


async def connect_db() -> asyncpg.Pool:
    """
    Создание подключения к базе данных PostgreSQL
    
    Returns:
        asyncpg.Pool: Пул соединений с базой данных
        
    Raises:
        ValueError: Если не найдены необходимые переменные окружения
        asyncpg.PostgresError: При ошибке подключения к БД
    """
    global pool
    
    if not DATABASE_URL and not all([DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST]):
        raise ValueError("Необходимо указать DATABASE_URL или комбинацию DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST")
    
    try:
        if DATABASE_URL:
            # Используем полный URL подключения
            pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
        else:
            # Собираем URL из отдельных компонентов
            database_url = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
            pool = await asyncpg.create_pool(
                database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
        
        logger.info("Успешное подключение к базе данных PostgreSQL")
        
        # Создаем таблицы при первом подключении
        await create_tables()
        
        return pool
        
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise


async def disconnect_db():
    """
    Закрытие подключения к базе данных
    """
    global pool
    
    if pool:
        await pool.close()
        pool = None
        logger.info("Подключение к базе данных закрыто")


async def create_tables():
    """
    Создание необходимых таблиц в базе данных
    """
    if not pool:
        raise RuntimeError("База данных не подключена. Вызовите connect_db() сначала.")
    
    async with pool.acquire() as connection:
        # Создание таблицы users
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                sub_ids BIGINT[] DEFAULT '{}',
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Создание индекса для быстрого поиска по email
        await connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE email IS NOT NULL
        """)
        
        # Создание функции для автоматического обновления updated_at
        await connection.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)
        
        # Создание триггера для автоматического обновления updated_at
        await connection.execute("""
            DROP TRIGGER IF EXISTS update_users_updated_at ON users;
            CREATE TRIGGER update_users_updated_at
                BEFORE UPDATE ON users
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
        """)
        
        logger.info("Таблицы созданы успешно")


async def create_user(id: int, sub_id: int, email: Optional[str] = None) -> bool:
    """
    Создание нового пользователя
    
    Args:
        id: ID пользователя из Telegram (bigint)
        sub_id: ID суб-аккаунта (bigint)
        email: Email пользователя (может быть None)
        
    Returns:
        bool: True если пользователь создан успешно, False если уже существует
        
    Raises:
        RuntimeError: Если база данных не подключена
        asyncpg.PostgresError: При ошибке выполнения запроса
    """
    if not pool:
        raise RuntimeError("База данных не подключена. Вызовите connect_db() сначала.")
    
    try:
        async with pool.acquire() as connection:
            # Проверяем, существует ли пользователь
            existing_user = await connection.fetchrow(
                "SELECT id FROM users WHERE id = $1", id
            )
            
            if existing_user:
                logger.warning(f"Пользователь с ID {id} уже существует")
                return False
            
            # Создаем нового пользователя
            await connection.execute("""
                INSERT INTO users (id, sub_ids, email)
                VALUES ($1, $2, $3)
            """, id, [sub_id], email)
            
            logger.info(f"Пользователь {id} создан успешно с суб-аккаунтом {sub_id}")
            return True
            
    except asyncpg.UniqueViolationError:
        logger.warning(f"Пользователь с ID {id} уже существует")
        return False
    except Exception as e:
        logger.error(f"Ошибка создания пользователя {id}: {e}")
        raise


async def update_user_add_sub(id: int, new_sub_id: int) -> bool:
    """
    Добавление нового суб-аккаунта пользователю
    
    Args:
        id: ID пользователя
        new_sub_id: ID нового суб-аккаунта
        
    Returns:
        bool: True если суб-аккаунт добавлен успешно, False если пользователь не найден
        
    Raises:
        RuntimeError: Если база данных не подключена
        asyncpg.PostgresError: При ошибке выполнения запроса
    """
    if not pool:
        raise RuntimeError("База данных не подключена. Вызовите connect_db() сначала.")
    
    try:
        async with pool.acquire() as connection:
            # Проверяем, существует ли пользователь
            user = await connection.fetchrow(
                "SELECT sub_ids FROM users WHERE id = $1", id
            )
            
            if not user:
                logger.warning(f"Пользователь с ID {id} не найден")
                return False
            
            # Проверяем, не существует ли уже такой суб-аккаунт
            current_sub_ids = user['sub_ids'] or []
            if new_sub_id in current_sub_ids:
                logger.warning(f"Суб-аккаунт {new_sub_id} уже существует у пользователя {id}")
                return False
            
            # Добавляем новый суб-аккаунт
            new_sub_ids = current_sub_ids + [new_sub_id]
            await connection.execute("""
                UPDATE users 
                SET sub_ids = $1 
                WHERE id = $2
            """, new_sub_ids, id)
            
            logger.info(f"Суб-аккаунт {new_sub_id} добавлен пользователю {id}")
            return True
            
    except Exception as e:
        logger.error(f"Ошибка добавления суб-аккаунта {new_sub_id} пользователю {id}: {e}")
        raise


async def update_user_email(id: int, email: str) -> bool:
    """
    Обновление или установка email пользователя
    
    Args:
        id: ID пользователя
        email: Новый email
        
    Returns:
        bool: True если email обновлен успешно, False если пользователь не найден
        
    Raises:
        RuntimeError: Если база данных не подключена
        asyncpg.PostgresError: При ошибке выполнения запроса
    """
    if not pool:
        raise RuntimeError("База данных не подключена. Вызовите connect_db() сначала.")
    
    try:
        async with pool.acquire() as connection:
            # Проверяем, существует ли пользователь
            user = await connection.fetchrow(
                "SELECT id FROM users WHERE id = $1", id
            )
            
            if not user:
                logger.warning(f"Пользователь с ID {id} не найден")
                return False
            
            # Обновляем email
            await connection.execute("""
                UPDATE users 
                SET email = $1 
                WHERE id = $2
            """, email, id)
            
            logger.info(f"Email пользователя {id} обновлен на {email}")
            return True
            
    except Exception as e:
        logger.error(f"Ошибка обновления email пользователя {id}: {e}")
        raise


async def get_user(id: int) -> Optional[Dict[str, Any]]:
    """
    Получение данных пользователя
    
    Args:
        id: ID пользователя
        
    Returns:
        Dict с данными пользователя или None если не найден
        
    Raises:
        RuntimeError: Если база данных не подключена
        asyncpg.PostgresError: При ошибке выполнения запроса
    """
    if not pool:
        raise RuntimeError("База данных не подключена. Вызовите connect_db() сначала.")
    
    try:
        async with pool.acquire() as connection:
            user = await connection.fetchrow("""
                SELECT id, sub_ids, email, created_at, updated_at
                FROM users 
                WHERE id = $1
            """, id)
            
            if not user:
                logger.info(f"Пользователь с ID {id} не найден")
                return None
            
            return {
                'id': user['id'],
                'sub_ids': user['sub_ids'] or [],
                'email': user['email'],
                'created_at': user['created_at'],
                'updated_at': user['updated_at']
            }
            
    except Exception as e:
        logger.error(f"Ошибка получения пользователя {id}: {e}")
        raise


async def get_all_users() -> List[Dict[str, Any]]:
    """
    Получение списка всех пользователей
    
    Returns:
        List[Dict]: Список всех пользователей
        
    Raises:
        RuntimeError: Если база данных не подключена
        asyncpg.PostgresError: При ошибке выполнения запроса
    """
    if not pool:
        raise RuntimeError("База данных не подключена. Вызовите connect_db() сначала.")
    
    try:
        async with pool.acquire() as connection:
            users = await connection.fetch("""
                SELECT id, sub_ids, email, created_at, updated_at
                FROM users 
                ORDER BY created_at DESC
            """)
            
            result = []
            for user in users:
                result.append({
                    'id': user['id'],
                    'sub_ids': user['sub_ids'] or [],
                    'email': user['email'],
                    'created_at': user['created_at'],
                    'updated_at': user['updated_at']
                })
            
            logger.info(f"Получено {len(result)} пользователей")
            return result
            
    except Exception as e:
        logger.error(f"Ошибка получения всех пользователей: {e}")
        raise


# Пример использования
async def main():
    """Пример использования функций базы данных"""
    try:
        # Подключение к базе данных
        await connect_db()
        
        # Создание пользователя
        success = await create_user(123456789, 987654321, "user@example.com")
        print(f"Создание пользователя: {success}")
        
        # Добавление суб-аккаунта
        success = await update_user_add_sub(123456789, 111222333)
        print(f"Добавление суб-аккаунта: {success}")
        
        # Обновление email
        success = await update_user_email(123456789, "newemail@example.com")
        print(f"Обновление email: {success}")
        
        # Получение пользователя
        user = await get_user(123456789)
        print(f"Данные пользователя: {user}")
        
        # Получение всех пользователей
        all_users = await get_all_users()
        print(f"Всего пользователей: {len(all_users)}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        # Отключение от базы данных
        await disconnect_db()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

