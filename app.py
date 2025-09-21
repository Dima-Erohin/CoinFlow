"""
FastAPI приложение для управления пользователями и их суб-аккаунтами.
Включает полный CRUD функционал для работы с базой данных.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import logging
import db


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="User Management API",
    description="API для управления пользователями и их суб-аккаунтами",
    version="1.0.0"
)

# Pydantic модели для валидации данных
class UserCreate(BaseModel):
    sub_id: int
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    sub_ids: List[int]
    email: Optional[str]
    created_at: str
    updated_at: str

class SubAccountAdd(BaseModel):
    new_sub_id: int

class EmailUpdate(BaseModel):
    email: str

class SuccessResponse(BaseModel):
    success: bool
    message: str

# События приложения
@app.on_event("startup")
async def startup_event():
    """Инициализация базы данных при запуске приложения"""
    try:
        await db.connect_db()
        logger.info("База данных подключена успешно")
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие соединения с базой данных при остановке приложения"""
    try:
        await db.disconnect_db()
        logger.info("Соединение с базой данных закрыто")
    except Exception as e:
        logger.error(f"Ошибка при закрытии соединения: {e}")

# Обработчики ошибок
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": str(exc), "success": False}
    )

@app.exception_handler(RuntimeError)
async def runtime_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Ошибка базы данных", "success": False}
    )

# API эндпоинты

@app.get("/", response_model=dict)
async def root():
    """Корневой эндпоинт с информацией об API"""
    return {
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

@app.get("/users", response_model=List[UserResponse])
async def get_all_users():
    """
    Получение списка всех пользователей
    
    Returns:
        List[UserResponse]: Список всех пользователей
    """
    try:
        users = await db.get_all_users()
        
        # Преобразуем datetime в строки для JSON сериализации
        result = []
        for user in users:
            result.append(UserResponse(
                id=user['id'],
                sub_ids=user['sub_ids'],
                email=user['email'],
                created_at=user['created_at'].isoformat(),
                updated_at=user['updated_at'].isoformat()
            ))
        
        logger.info(f"Получено {len(result)} пользователей")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка получения пользователей: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения пользователей"
        )

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """
    Получение пользователя по ID
    
    Args:
        user_id: ID пользователя
        
    Returns:
        UserResponse: Данные пользователя
        
    Raises:
        HTTPException: Если пользователь не найден
    """
    try:
        user = await db.get_user(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {user_id} не найден"
            )
        
        return UserResponse(
            id=user['id'],
            sub_ids=user['sub_ids'],
            email=user['email'],
            created_at=user['created_at'].isoformat(),
            updated_at=user['updated_at'].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения пользователя {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения пользователя"
        )

@app.post("/users", response_model=SuccessResponse)
async def create_user(user_id: int, user_data: UserCreate):
    """
    Создание нового пользователя
    
    Args:
        user_id: ID пользователя из Telegram
        user_data: Данные пользователя (sub_id, email)
        
    Returns:
        SuccessResponse: Результат операции
        
    Raises:
        HTTPException: Если пользователь уже существует
    """
    try:
        success = await db.create_user(
            id=user_id,
            sub_id=user_data.sub_id,
            email=user_data.email
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Пользователь с ID {user_id} уже существует"
            )
        
        logger.info(f"Пользователь {user_id} создан успешно")
        return SuccessResponse(
            success=True,
            message=f"Пользователь {user_id} создан успешно"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка создания пользователя {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка создания пользователя"
        )

@app.put("/users/{user_id}/sub-accounts", response_model=SuccessResponse)
async def add_sub_account(user_id: int, sub_data: SubAccountAdd):
    """
    Добавление суб-аккаунта пользователю
    
    Args:
        user_id: ID пользователя
        sub_data: Данные суб-аккаунта (new_sub_id)
        
    Returns:
        SuccessResponse: Результат операции
        
    Raises:
        HTTPException: Если пользователь не найден или суб-аккаунт уже существует
    """
    try:
        success = await db.update_user_add_sub(user_id, sub_data.new_sub_id)
        
        if not success:
            # Проверяем, существует ли пользователь
            user = await db.get_user(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Пользователь с ID {user_id} не найден"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Суб-аккаунт {sub_data.new_sub_id} уже существует у пользователя {user_id}"
                )
        
        logger.info(f"Суб-аккаунт {sub_data.new_sub_id} добавлен пользователю {user_id}")
        return SuccessResponse(
            success=True,
            message=f"Суб-аккаунт {sub_data.new_sub_id} добавлен пользователю {user_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка добавления суб-аккаунта {sub_data.new_sub_id} пользователю {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка добавления суб-аккаунта"
        )

@app.put("/users/{user_id}/email", response_model=SuccessResponse)
async def update_user_email(user_id: int, email_data: EmailUpdate):
    """
    Обновление email пользователя
    
    Args:
        user_id: ID пользователя
        email_data: Новый email
        
    Returns:
        SuccessResponse: Результат операции
        
    Raises:
        HTTPException: Если пользователь не найден
    """
    try:
        success = await db.update_user_email(user_id, email_data.email)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с ID {user_id} не найден"
            )
        
        logger.info(f"Email пользователя {user_id} обновлен на {email_data.email}")
        return SuccessResponse(
            success=True,
            message=f"Email пользователя {user_id} обновлен успешно"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления email пользователя {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обновления email"
        )

# Дополнительные эндпоинты для совместимости с существующим кодом

@app.get("/user/{user_id}")
async def get_user_legacy(user_id: int):
    """
    Legacy эндпоинт для получения пользователя (совместимость)
    """
    user = await get_user(user_id)
    return {
        "id": user.id,
        "Sub-IDs": user.sub_ids,
        "Email": user.email,
        "Создан": user.created_at,
        "Обновлен": user.updated_at
    }

@app.post("/user-create/{user_id}")
async def add_user_legacy(user_id: int):
    """
    Legacy эндпоинт для создания пользователя (совместимость)
    """
    user_data = UserCreate(sub_id=123, email="email")
    return await create_user(user_id, user_data)

@app.post("/user/{user_id}/cards")
async def add_card(user_id: int):
    """
    Эндпоинт для создания карты (заглушка)
    """
    logger.info(f"Запрос на создание карты для пользователя {user_id}")
    return {"user_id": user_id, "message": "card created"}

@app.get("/user/{user_id}/cards")
async def get_cards(user_id: int):
    """
    Эндпоинт для получения карт пользователя (заглушка)
    """
    logger.info(f"Запрос на получение карт пользователя {user_id}")
    return {"user_id": user_id, "cards": []}

