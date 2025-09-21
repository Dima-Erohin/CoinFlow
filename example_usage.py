"""
Пример использования модуля payments.py
Демонстрирует основные функции для работы с платежами
"""

import os
from payments.payments import (
    create_transaction, 
    deposit_via_stripe, 
    get_user_transactions, 
    get_user_balance,
    confirm_stripe_payment,
    ledger
)

def main():
    """Основная функция с примерами использования"""
    
    print("=== Демонстрация работы с платежами ===\n")
    
    # Проверяем настройку API
    print("🔍 Проверка конфигурации API:")
    print(f"   NonameCards API: {'✅ Настроен' if os.getenv('NONAME_API_KEY') else '❌ Не настроен'}")
    
    # Проверяем Stripe более детально
    stripe_key = os.getenv('STRIPE_SECRET_KEY')
    if stripe_key:
        if stripe_key.startswith('sk_test_') or stripe_key.startswith('sk_live_'):
            print(f"   Stripe API: ✅ Настроен (ключ: {stripe_key[:10]}...)")
        else:
            print(f"   Stripe API: ⚠️ Ключ задан, но неверный формат")
    else:
        print(f"   Stripe API: ❌ Не настроен")
    print()
    
    # Пример 1: Транзакция между картами
    print("1. Создание транзакции между картами:")
    result = create_transaction(
        from_card_id="card_123456",
        to_card_id="card_789012",
        amount=100.0,
        user_id="user_001"
    )
    print(f"   Результат: {result}\n")
    
    # Пример 2: Ввод средств через Stripe Checkout
    print("2. Создание Checkout Session для ввода средств:")
    result = deposit_via_stripe(
        user_id="user_001",
        amount=50.0,
        success_url="https://example.com/success",
        cancel_url="https://example.com/cancel"
    )
    print(f"   Результат: {result}\n")
    
    # Пример 3: Ввод средств через PaymentIntent
    print("3. Создание PaymentIntent для ввода средств:")
    result = deposit_via_stripe(
        user_id="user_002",
        amount=25.0
    )
    print(f"   Результат: {result}\n")
    
    # Пример 4: Получение транзакций пользователя
    print("4. Транзакции пользователя user_001:")
    transactions = get_user_transactions("user_001")
    for tx in transactions:
        print(f"   - {tx['type']}: ${tx['gross']:.2f} (статус: {tx['status']})")
    print()
    
    # Пример 5: Получение баланса пользователя
    print("5. Баланс пользователя user_001:")
    balance = get_user_balance("user_001")
    print(f"   Баланс: ${balance['balance']:.2f}")
    print(f"   Всего депозитов: ${balance['total_deposits']:.2f}")
    print(f"   Всего переводов: ${balance['total_transfers']:.2f}")
    print(f"   Количество транзакций: {balance['transaction_count']}\n")
    
    # Пример 6: Подтверждение Stripe платежа (симуляция)
    print("6. Подтверждение Stripe платежа:")
    # В реальном приложении payment_intent_id приходит от Stripe webhook
    payment_intent_id = "pi_test_1234567890"
    result = confirm_stripe_payment(payment_intent_id)
    print(f"   Результат: {result}\n")
    
    # Пример 7: Просмотр всех транзакций в Ledger
    print("7. Все транзакции в системе:")
    all_transactions = ledger.transactions
    for tx in all_transactions:
        print(f"   {tx.id}: {tx.user_id} - {tx.type.value} - ${tx.gross:.2f} ({tx.status.value})")
    
    print(f"\nВсего транзакций в системе: {len(all_transactions)}")


def test_error_handling():
    """Тестирование обработки ошибок"""
    print("\n=== Тестирование обработки ошибок ===\n")
    
    # Тест без API ключей
    print("1. Тест без настроенных API ключей:")
    result = create_transaction("card_1", "card_2", 10.0, "user_test")
    print(f"   Результат: {result}\n")
    
    result = deposit_via_stripe("user_test", 10.0)
    print(f"   Результат: {result}\n")


if __name__ == "__main__":
    # Запуск основных примеров
    main()
    
    # Запуск тестов обработки ошибок
    test_error_handling()
    
    print("\n=== Инструкции по настройке ===")
    print("1. Создайте файл .env в корне проекта")
    print("2. Добавьте следующие переменные:")
    print("   STRIPE_SECRET_KEY=sk_test_your_key_here")
    print("   NONAME_API_KEY=your_api_key_here")
    print("   NONAME_API_BASE_URL=https://api.nonamecards.com")
    print("3. Установите зависимости: pip install -r requirements.txt")
    print("4. Запустите: python example_usage.py")
    print("\n💡 Для тестирования без реальных API ключей:")
    print("   - Функции будут возвращать ошибки о ненастроенных API")
    print("   - Это нормальное поведение для демонстрации")
    print("   - Ledger будет работать и сохранять транзакции в файл")

