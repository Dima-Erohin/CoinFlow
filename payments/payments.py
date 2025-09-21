"""
Модуль для работы с платежами через Stripe API.
Включает в себя функции для транзакций между картами, ввода средств и ведения учёта.
"""

import os
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Безопасный импорт Stripe
STRIPE_AVAILABLE = False

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    stripe = None
    STRIPE_AVAILABLE = False


# Конфигурация
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')

# Инициализация Stripe
STRIPE_INITIALIZED = False
if STRIPE_AVAILABLE and STRIPE_SECRET_KEY and STRIPE_SECRET_KEY.startswith('sk_'):
    try:
        stripe.api_key = STRIPE_SECRET_KEY
        STRIPE_INITIALIZED = True
        print(f"Stripe инициализирован с ключом: {STRIPE_SECRET_KEY[:10]}...")
    except Exception as e:
        print(f"Ошибка инициализации Stripe: {e}")
        STRIPE_INITIALIZED = False
else:
    print("Stripe не инициализирован")


class TransactionType(Enum):
    """Типы транзакций"""
    STRIPE_DEPOSIT = "stripe_deposit"
    CARD_TO_CARD = "card_to_card"
    CARD_WITHDRAWAL = "card_withdrawal"


class TransactionStatus(Enum):
    """Статусы транзакций"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Transaction:
    """Модель транзакции для Ledger"""
    id: str
    user_id: str
    type: TransactionType
    gross: float
    net: float
    fee: float
    status: TransactionStatus
    timestamp: datetime
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Преобразование в словарь для сериализации"""
        data = asdict(self)
        data['type'] = self.type.value
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


class Ledger:
    """Класс для ведения учёта всех транзакций"""
    
    def __init__(self, storage_file: str = "transactions.json"):
        self.storage_file = storage_file
        self.transactions: List[Transaction] = []
        self._load_transactions()
    
    def _load_transactions(self):
        """Загрузка транзакций из файла"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        transaction = Transaction(
                            id=item['id'],
                            user_id=item['user_id'],
                            type=TransactionType(item['type']),
                            gross=item['gross'],
                            net=item['net'],
                            fee=item['fee'],
                            status=TransactionStatus(item['status']),
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            metadata=item.get('metadata')
                        )
                        self.transactions.append(transaction)
            except Exception as e:
                print(f"Ошибка загрузки транзакций: {e}")
    
    def _save_transactions(self):
        """Сохранение транзакций в файл"""
        try:
            data = [tx.to_dict() for tx in self.transactions]
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения транзакций: {e}")
    
    def log_transaction(self, user_id: str, transaction_type: TransactionType, 
                       gross: float, net: float, fee: float, 
                       status: TransactionStatus, metadata: Optional[Dict] = None) -> str:
        """Логирование новой транзакции"""
        transaction_id = str(uuid.uuid4())
        transaction = Transaction(
            id=transaction_id,
            user_id=user_id,
            type=transaction_type,
            gross=gross,
            net=net,
            fee=fee,
            status=status,
            timestamp=datetime.now(),
            metadata=metadata
        )
        
        self.transactions.append(transaction)
        self._save_transactions()
        return transaction_id
    
    def get_transactions(self, user_id: str) -> List[Transaction]:
        """Получение всех транзакций пользователя"""
        return [tx for tx in self.transactions if tx.user_id == user_id]
    
    def update_transaction_status(self, transaction_id: str, status: TransactionStatus):
        """Обновление статуса транзакции"""
        for tx in self.transactions:
            if tx.id == transaction_id:
                tx.status = status
                self._save_transactions()
                break


class StripePayments:
    """Класс для работы с Stripe API"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.initialized = STRIPE_INITIALIZED and STRIPE_AVAILABLE
    
    def create_payment_intent(self, amount: float, currency: str = 'usd', 
                            metadata: Optional[Dict] = None) -> Dict:
        """Создание PaymentIntent для ввода средств"""
        if not self.initialized:
            return {
                'success': False,
                'error': 'Stripe API не инициализирован'
            }
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe работает с центами
                currency=currency,
                metadata=metadata or {}
            )
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': intent.amount,
                'status': intent.status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_checkout_session(self, amount: float, user_id: str, 
                              success_url: str, cancel_url: str) -> Dict:
        """Создание Checkout Session для ввода средств"""
        if not self.initialized:
            return {
                'success': False,
                'error': 'Stripe API не инициализирован'
            }
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Пополнение баланса',
                        },
                        'unit_amount': int(amount * 100),  # В центах
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={'user_id': user_id}
            )
            return {
                'success': True,
                'session_id': session.id,
                'url': session.url
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def retrieve_payment_intent(self, payment_intent_id: str) -> Dict:
        """Получение информации о PaymentIntent"""
        if not self.initialized:
            return {
                'success': False,
                'error': 'Stripe API не инициализирован'
            }
        
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'success': True,
                'status': intent.status,
                'amount': intent.amount,
                'metadata': intent.metadata
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_transfer(self, amount: float, destination_account: str, 
                       source_transaction: str = None, metadata: Optional[Dict] = None) -> Dict:
        """Создание перевода через Stripe Connect"""
        if not self.initialized:
            return {
                'success': False,
                'error': 'Stripe API не инициализирован'
            }
        
        try:
            transfer = stripe.Transfer.create(
                amount=int(amount * 100),  # В центах
                currency='usd',
                destination=destination_account,
                source_transaction=source_transaction,
                metadata=metadata or {}
            )
            return {
                'success': True,
                'transfer_id': transfer.id,
                'amount': transfer.amount,
                'status': transfer.status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_charge(self, amount: float, source: str, 
                     description: str = None, metadata: Optional[Dict] = None) -> Dict:
        """Создание списания с карты"""
        if not self.initialized:
            return {
                'success': False,
                'error': 'Stripe API не инициализирован'
            }
        
        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # В центах
                currency='usd',
                source=source,
                description=description,
                metadata=metadata or {}
            )
            return {
                'success': True,
                'charge_id': charge.id,
                'amount': charge.amount,
                'status': charge.status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Глобальные экземпляры
ledger = Ledger()
stripe_payments = StripePayments(STRIPE_SECRET_KEY) if STRIPE_SECRET_KEY and STRIPE_AVAILABLE else None


def deposit_via_stripe(user_id: str, amount: float, 
                      success_url: str = None, cancel_url: str = None) -> Dict:
    """Ввод средств через Stripe"""
    if not stripe_payments:
        return {
            'success': False,
            'error': 'Stripe API не настроен. Установите STRIPE_SECRET_KEY в переменных окружения.'
        }
    
    # Логируем транзакцию как pending
    fee = amount * 0.029 + 0.30  # Stripe комиссия: 2.9% + $0.30
    net_amount = amount - fee
    
    transaction_id = ledger.log_transaction(
        user_id=user_id,
        transaction_type=TransactionType.STRIPE_DEPOSIT,
        gross=amount,
        net=net_amount,
        fee=fee,
        status=TransactionStatus.PENDING,
        metadata={'amount': amount}
    )
    
    # Создаём Checkout Session или PaymentIntent
    if success_url and cancel_url:
        result = stripe_payments.create_checkout_session(
            amount=amount,
            user_id=user_id,
            success_url=success_url,
            cancel_url=cancel_url
        )
    else:
        result = stripe_payments.create_payment_intent(
            amount=amount,
            metadata={'user_id': user_id, 'transaction_id': transaction_id}
        )
    
    if result['success']:
        result['transaction_id'] = transaction_id
    else:
        ledger.update_transaction_status(transaction_id, TransactionStatus.FAILED)
        result['transaction_id'] = transaction_id
    
    return result


def create_card_to_card_transaction(user_id: str, amount: float, from_payment_method: str, to_payment_method: str):
    """
    Перевод между картами (эмуляция через Stripe PaymentIntent).
    В реальном проекте нужен Stripe Connect.
    """
    transaction_id = str(uuid.uuid4())
    try:
        if not STRIPE_AVAILABLE or not STRIPE_SECRET_KEY:
            raise ValueError("Stripe не настроен")

        # Создаём PaymentIntent на списание
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # в центах
            currency="usd",
            automatic_payment_methods={'enabled': True}
        )

        # Для теста считаем перевод успешным
        ledger.log_transaction(user_id, TransactionType.CARD_TO_CARD, amount, amount, 0.0, TransactionStatus.COMPLETED)

        return {
            "success": True,
            "transaction_id": transaction_id,
            "payment_intent_id": payment_intent.id
        }

    except Exception as e:
        ledger.log_transaction(user_id, TransactionType.CARD_TO_CARD, amount, amount, 0.0, TransactionStatus.FAILED)
        return {"success": False, "error": str(e), "transaction_id": transaction_id}




def confirm_stripe_payment(payment_intent_id: str) -> Dict:
    """Подтверждение успешного платежа Stripe"""
    if not stripe_payments:
        return {
            'success': False,
            'error': 'Stripe API не настроен. Установите STRIPE_SECRET_KEY в переменных окружения.'
        }
    
    result = stripe_payments.retrieve_payment_intent(payment_intent_id)
    
    if result['success'] and result['status'] == 'succeeded':
        # Обновляем статус транзакции
        user_id = result['metadata'].get('user_id')
        transaction_id = result['metadata'].get('transaction_id')
        
        if transaction_id:
            ledger.update_transaction_status(transaction_id, TransactionStatus.COMPLETED)
        
        return {
            'success': True,
            'message': 'Платеж успешно подтвержден',
            'user_id': user_id,
            'transaction_id': transaction_id
        }
    
    return {
        'success': False,
        'error': 'Платеж не найден или не завершен'
    }


def get_user_transactions(user_id: str) -> List[Dict]:
    """Получение всех транзакций пользователя"""
    transactions = ledger.get_transactions(user_id)
    return [tx.to_dict() for tx in transactions]


def get_user_balance(user_id: str) -> Dict:
    """Получение баланса пользователя на основе транзакций"""
    transactions = ledger.get_transactions(user_id)
    
    total_deposits = sum(tx.net for tx in transactions 
                        if tx.type == TransactionType.STRIPE_DEPOSIT 
                        and tx.status == TransactionStatus.COMPLETED)
    
    total_transfers_out = sum(tx.gross for tx in transactions 
                             if tx.type == TransactionType.CARD_TO_CARD 
                             and tx.status == TransactionStatus.COMPLETED)
    
    balance = total_deposits - total_transfers_out
    
    return {
        'user_id': user_id,
        'balance': balance,
        'total_deposits': total_deposits,
        'total_transfers': total_transfers_out,
        'transaction_count': len(transactions)
    }


# Пример использования
if __name__ == "__main__":
    # Пример ввода средств через Stripe
    print("=== Пример ввода средств через Stripe ===")
    result = deposit_via_stripe(
        user_id="user_001",
        amount=50.0,
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel"
    )
    print(f"Результат ввода средств: {result}")
    
    # Пример транзакции с карты на карту
    print("\n=== Пример транзакции с карты на карту ===")
    result = create_card_to_card_transaction("user_001",
                                             100.0,
                                             "pm_card_visa",
                                             "pm_card_mastercard")
    print(f"Результат транзакции: {result}")
    
    # Получение транзакций пользователя
    print("\n=== Транзакции пользователя ===")
    transactions = get_user_transactions("user_001")
    for tx in transactions:
        print(f"Транзакция {tx['id']}: {tx['type']} - ${tx['gross']} (статус: {tx['status']})")
    
    # Получение баланса пользователя
    print("\n=== Баланс пользователя ===")
    balance = get_user_balance("user_001")
    print(f"Баланс пользователя {balance['user_id']}: ${balance['balance']:.2f}")