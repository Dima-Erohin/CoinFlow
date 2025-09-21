"""
Пример использования модуля payments.py
Демонстрирует основные функции для работы с платежами
"""

import os
from payments.payments import (
    create_card_to_card_transaction,
    deposit_via_stripe,
    get_user_transactions,
    get_user_balance,
    confirm_stripe_payment,
    ledger,
    TransactionStatus
)

def main():
    """Основная функция с примерами использования"""

    print("=== Демонстрация работы с платежами ===\n")

    # Проверяем настройку API
    print("🔍 Проверка конфигурации API:")
    print(f"   Stripe API: {'✅ Настроен' if os.getenv('STRIPE_SECRET_KEY') else '❌ Не настроен'}")
    print()

    # Пример 1: Транзакция между картами
    print("1. Создание транзакции между картами:")
    # пример после вызова create_card_to_card_transaction
    result = create_card_to_card_transaction("user_001",
                                             100.0,
                                             "pm_card_visa",
                                             "pm_card_mastercard")
    if result["success"]:
        ledger.update_transaction_status(result["transaction_id"], TransactionStatus.COMPLETED)

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
    result = create_card_to_card_transaction("user_001",
                                             100.0,
                                             "pm_card_visa",
                                             "pm_card_mastercard")
    print(f"   Результат: {result}\n")

    result = deposit_via_stripe("user_test", 10.0)
    print(f"   Результат: {result}\n")


if __name__ == "__main__":
    main()
    test_error_handling()

    print("\n=== Инструкции по настройке ===")
    print("1. Создайте файл .env в корне проекта")
    print("2. Добавьте следующие переменные:")
    print("   STRIPE_SECRET_KEY=sk_test_your_key_here")
    print("3. Установите зависимости: pip install -r requirements.txt")
    print("4. Запустите: python example_usage.py")
    print("\n💡 Для тестирования без реальных API ключей:")
    print("   - Функции будут возвращать ошибки о ненастроенном API")
    print("   - Это нормальное поведение для демонстрации")
    print("   - Ledger будет работать и сохранять транзакции в файл")