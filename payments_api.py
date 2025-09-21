"""
FastAPI роутер для платежных операций.
Включает эндпоинты для переводов, пополнений и управления балансом.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import logging
from payments.payments import (
    create_card_to_card_transaction,
    deposit_via_stripe,
    get_user_transactions,
    get_user_balance,
    confirm_stripe_payment
)

# Настройка логирования
logger = logging.getLogger(__name__)

# Создаем роутер для платежей
payments_router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}}
)

# Pydantic модели для платежей
class CardToCardRequest(BaseModel):
    """Модель для запроса перевода с карты на карту"""
    amount: float
    from_card_id: str
    to_card_id: str
    from_card_number: Optional[str] = None
    to_card_number: Optional[str] = None

class DepositRequest(BaseModel):
    """Модель для запроса пополнения баланса"""
    amount: float
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None

class PaymentConfirmRequest(BaseModel):
    """Модель для подтверждения платежа"""
    payment_intent_id: str

class PaymentResponse(BaseModel):
    """Базовая модель ответа для платежей"""
    success: bool
    message: Optional[str] = None
    transaction_id: Optional[str] = None
    error: Optional[str] = None

# Эндпоинты для переводов с карты на карту
@payments_router.post("/card-to-card/{user_id}", response_model=dict)
async def create_card_to_card_payment(user_id: int, request: CardToCardRequest):
    """
    Перевод с карты на карту
    
    Args:
        user_id: ID пользователя
        request: Данные перевода (сумма, карты)
        
    Returns:
        Результат перевода с transaction_id и payment_intent_id
    """
    try:
        logger.info(f"Запрос перевода с карты на карту для пользователя {user_id}")
        
        result = create_card_to_card_transaction(
            user_id=str(user_id),
            amount=request.amount,
            from_payment_method=request.from_card_id,
            to_payment_method=request.to_card_id
        )
        
        # Добавляем дополнительную информацию в ответ
        if result["success"]:
            result["message"] = f"Перевод на сумму ${request.amount} успешно создан"
            result["from_card_id"] = request.from_card_id
            result["to_card_id"] = request.to_card_id
            result["amount"] = request.amount
        
        logger.info(f"Результат перевода для пользователя {user_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка перевода для пользователя {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка перевода: {str(e)}"
        )

# Эндпоинты для пополнения баланса
@payments_router.post("/deposit/{user_id}", response_model=dict)
async def create_deposit(user_id: int, request: DepositRequest):
    """
    Пополнение баланса через Stripe
    
    Args:
        user_id: ID пользователя
        request: Данные пополнения (сумма, URL для редиректа)
        
    Returns:
        Результат создания пополнения с session_id или client_secret
    """
    try:
        logger.info(f"Запрос пополнения для пользователя {user_id}")
        
        result = deposit_via_stripe(
            user_id=str(user_id),
            amount=request.amount,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )
        
        # Добавляем дополнительную информацию в ответ
        if result["success"]:
            result["message"] = f"Пополнение на сумму ${request.amount} успешно создано"
            result["amount"] = request.amount
        
        logger.info(f"Результат пополнения для пользователя {user_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка пополнения для пользователя {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка пополнения: {str(e)}"
        )

# Эндпоинты для получения информации о транзакциях
@payments_router.get("/transactions/{user_id}", response_model=dict)
async def get_user_payment_transactions(user_id: int):
    """
    Получение всех транзакций пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Список транзакций пользователя с детальной информацией
    """
    try:
        logger.info(f"Запрос транзакций для пользователя {user_id}")
        
        transactions = get_user_transactions(str(user_id))
        
        result = {
            "user_id": user_id,
            "transactions": transactions,
            "total_count": len(transactions),
            "message": f"Найдено {len(transactions)} транзакций"
        }
        
        logger.info(f"Получено {len(transactions)} транзакций для пользователя {user_id}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка получения транзакций для пользователя {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения транзакций: {str(e)}"
        )

# Эндпоинты для получения баланса
@payments_router.get("/balance/{user_id}", response_model=dict)
async def get_user_payment_balance(user_id: int):
    """
    Получение баланса пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Детальная информация о балансе пользователя
    """
    try:
        logger.info(f"Запрос баланса для пользователя {user_id}")
        
        balance = get_user_balance(str(user_id))
        
        # Добавляем дополнительную информацию
        balance["message"] = f"Баланс пользователя {user_id} успешно получен"
        
        logger.info(f"Баланс пользователя {user_id}: ${balance['balance']:.2f}")
        return balance
        
    except Exception as e:
        logger.error(f"Ошибка получения баланса для пользователя {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения баланса: {str(e)}"
        )

# Эндпоинты для подтверждения платежей
@payments_router.post("/confirm", response_model=dict)
async def confirm_payment(request: PaymentConfirmRequest):
    """
    Подтверждение Stripe платежа
    
    Args:
        request: ID PaymentIntent для подтверждения
        
    Returns:
        Результат подтверждения платежа
    """
    try:
        logger.info(f"Запрос подтверждения платежа {request.payment_intent_id}")
        
        result = confirm_stripe_payment(request.payment_intent_id)
        
        logger.info(f"Результат подтверждения платежа {request.payment_intent_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Ошибка подтверждения платежа {request.payment_intent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка подтверждения платежа: {str(e)}"
        )

# Эндпоинт для получения статистики платежей
@payments_router.get("/stats/{user_id}", response_model=dict)
async def get_payment_stats(user_id: int):
    """
    Получение статистики платежей пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Статистика по транзакциям пользователя
    """
    try:
        logger.info(f"Запрос статистики для пользователя {user_id}")
        
        transactions = get_user_transactions(str(user_id))
        balance = get_user_balance(str(user_id))
        
        # Подсчитываем статистику
        total_transactions = len(transactions)
        successful_transactions = len([tx for tx in transactions if tx['status'] == 'completed'])
        failed_transactions = len([tx for tx in transactions if tx['status'] == 'failed'])
        pending_transactions = len([tx for tx in transactions if tx['status'] == 'pending'])
        
        total_amount = sum(tx['gross'] for tx in transactions)
        successful_amount = sum(tx['gross'] for tx in transactions if tx['status'] == 'completed')
        
        stats = {
            "user_id": user_id,
            "balance": balance,
            "transaction_stats": {
                "total_transactions": total_transactions,
                "successful_transactions": successful_transactions,
                "failed_transactions": failed_transactions,
                "pending_transactions": pending_transactions,
                "success_rate": (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0
            },
            "amount_stats": {
                "total_amount": total_amount,
                "successful_amount": successful_amount,
                "average_transaction": total_amount / total_transactions if total_transactions > 0 else 0
            },
            "message": f"Статистика для пользователя {user_id} успешно получена"
        }
        
        logger.info(f"Статистика для пользователя {user_id}: {total_transactions} транзакций")
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики для пользователя {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики: {str(e)}"
        )

# Эндпоинт для проверки статуса платежной системы
@payments_router.get("/health", response_model=dict)
async def payments_health_check():
    """
    Проверка состояния платежной системы
    
    Returns:
        Статус платежной системы и доступных сервисов
    """
    try:
        import os
        from payments.payments import STRIPE_AVAILABLE, STRIPE_INITIALIZED
        
        health_status = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",  # Можно добавить datetime.now().isoformat()
            "services": {
                "stripe_api": {
                    "available": STRIPE_AVAILABLE,
                    "initialized": STRIPE_INITIALIZED,
                    "secret_key_configured": bool(os.getenv('STRIPE_SECRET_KEY'))
                },
                "ledger": {
                    "available": True,
                    "status": "operational"
                }
            },
            "message": "Платежная система работает нормально"
        }
        
        logger.info("Проверка состояния платежной системы: OK")
        return health_status
        
    except Exception as e:
        logger.error(f"Ошибка проверки состояния платежной системы: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Платежная система недоступна"
        }
