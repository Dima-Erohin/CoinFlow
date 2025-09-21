# Модуль платежей (payments.py)

Полноценный модуль для работы с платежами через NonameCards API и Stripe API, включающий ведение учёта всех транзакций.

## Возможности

- ✅ Транзакции между картами через NonameCards API
- ✅ Ввод средств через Stripe API (PaymentIntent и Checkout)
- ✅ Ведение учёта всех транзакций (Ledger)
- ✅ Автоматический расчёт комиссий
- ✅ Отслеживание статусов транзакций
- ✅ Получение баланса пользователей

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` в корне проекта:
```env
# Stripe API ключи
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here

# NonameCards API
NONAME_API_KEY=your_noname_api_key_here
NONAME_API_BASE_URL=https://api.nonamecards.com
```

## Основные классы

### Ledger
Класс для ведения учёта всех транзакций:
- `log_transaction()` - логирование новой транзакции
- `get_transactions(user_id)` - получение транзакций пользователя
- `update_transaction_status()` - обновление статуса транзакции

### NonameCardsAPI
Класс для работы с NonameCards API:
- `create_transfer()` - создание перевода между картами

### StripePayments
Класс для работы с Stripe API:
- `create_payment_intent()` - создание PaymentIntent
- `create_checkout_session()` - создание Checkout Session
- `retrieve_payment_intent()` - получение информации о платеже

## Основные функции

### create_transaction(from_card_id, to_card_id, amount, user_id)
Создание транзакции между картами через NonameCards API.

**Параметры:**
- `from_card_id` (str): ID карты отправителя
- `to_card_id` (str): ID карты получателя  
- `amount` (float): Сумма перевода
- `user_id` (str): ID пользователя

**Возвращает:**
```python
{
    'success': True/False,
    'data': {...},  # данные от API
    'transaction_id': 'uuid',
    'error': 'error_message'  # при ошибке
}
```

### deposit_via_stripe(user_id, amount, success_url=None, cancel_url=None)
Ввод средств через Stripe API.

**Параметры:**
- `user_id` (str): ID пользователя
- `amount` (float): Сумма для ввода
- `success_url` (str, optional): URL для успешного платежа
- `cancel_url` (str, optional): URL для отмены платежа

**Возвращает:**
```python
{
    'success': True/False,
    'client_secret': 'pi_xxx_secret_xxx',  # для PaymentIntent
    'url': 'https://checkout.stripe.com/...',  # для Checkout
    'transaction_id': 'uuid',
    'error': 'error_message'  # при ошибке
}
```

### get_user_transactions(user_id)
Получение всех транзакций пользователя.

### get_user_balance(user_id)
Получение баланса пользователя на основе транзакций.

### confirm_stripe_payment(payment_intent_id)
Подтверждение успешного Stripe платежа.

## Структура транзакции

Каждая транзакция содержит:
- `id`: Уникальный ID транзакции
- `user_id`: ID пользователя
- `type`: Тип транзакции (`stripe_deposit` или `card_transfer`)
- `gross`: Общая сумма
- `net`: Чистая сумма (после комиссии)
- `fee`: Размер комиссии
- `status`: Статус (`pending`, `completed`, `failed`, `cancelled`)
- `timestamp`: Время создания
- `metadata`: Дополнительные данные

## Комиссии

- **NonameCards**: 2% от суммы перевода
- **Stripe**: 2.9% + $0.30 за транзакцию

## Примеры использования

### Базовое использование
```python
from payments.payments import create_transaction, deposit_via_stripe

# Транзакция между картами
result = create_transaction(
    from_card_id="card_123",
    to_card_id="card_456",
    amount=100.0,
    user_id="user_001"
)

# Ввод средств через Stripe
result = deposit_via_stripe(
    user_id="user_001",
    amount=50.0,
    success_url="https://example.com/success",
    cancel_url="https://example.com/cancel"
)
```

### Получение информации
```python
from payments.payments import get_user_transactions, get_user_balance

# Получение транзакций
transactions = get_user_transactions("user_001")

# Получение баланса
balance = get_user_balance("user_001")
print(f"Баланс: ${balance['balance']:.2f}")
```

### Работа с Ledger
```python
from payments.payments import ledger

# Получение всех транзакций
all_transactions = ledger.transactions

# Обновление статуса
ledger.update_transaction_status("transaction_id", TransactionStatus.COMPLETED)
```

## Запуск примера

```bash
python example_usage.py
```

## Обработка ошибок

Модуль включает обработку следующих ошибок:
- Отсутствие API ключей
- Ошибки сети при запросах к API
- Неверные параметры
- Ошибки Stripe API

## Безопасность

- Все API ключи берутся из переменных окружения
- Транзакции логируются с полной информацией
- Поддержка тестовых ключей Stripe
- Валидация входных данных

## Расширение функционала

Для добавления новых типов транзакций:
1. Добавьте новый тип в `TransactionType` enum
2. Создайте соответствующую функцию
3. Обновите логику расчёта комиссий при необходимости

## Файлы

- `payments/payments.py` - основной модуль
- `example_usage.py` - примеры использования
- `requirements.txt` - зависимости
- `transactions.json` - файл с транзакциями (создается автоматически)


