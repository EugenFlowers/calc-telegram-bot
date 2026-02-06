import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ Добавьте BOT_TOKEN в Bothost.ru")
    exit(1)

# Этапы диалога
AMOUNT, MONTHS, RATE = range(3)


def calc_annuity_payment(amount: float, months: int, annual_rate: float) -> tuple[float, float, float]:
    """Возвращает (ежемесячный платёж, общая выплата, переплата)."""
    if months <= 0:
        raise ValueError("Срок должен быть > 0")
    if annual_rate < 0:
        raise ValueError("Ставка не может быть отрицательной")

    monthly_rate = annual_rate / 12 / 100  # i
    if monthly_rate == 0:
        monthly_payment = amount / months
    else:
        monthly_payment = amount * monthly_rate / (1 - (1 + monthly_rate) ** (-months))
    total_payment = monthly_payment * months
    overpayment = total_payment - amount
    return monthly_payment, total_payment, overpayment


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 Кредитный калькулятор.\n\n"
        "Введите сумму кредита в рублях (только число, без пробелов и знаков):\n"
        "💰 Например: 500000"
    )
    return AMOUNT


async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(" ", "")
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Введите корректную сумму (положительное число). Пример: 500000")
        return AMOUNT

    context.user_data["amount"] = amount
    await update.message.reply_text(
        f"✅ Сумма: {amount:,.2f} ₽\n\n"
        "⏳ Теперь введите срок кредита в месяцах:\n"
        "📅 Например: 12, 24, 36"
    )
    return MONTHS


async def months_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        months = int(text)
        if months <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Введите целое число месяцев > 0. Пример: 24")
        return MONTHS

    context.user_data["months"] = months
    await update.message.reply_text(
        f"✅ Срок: {months} месяцев\n\n"
        "📈 Введите годовую процентную ставку:\n"
        "📊 Например: 15 или 19.9"
    )
    return RATE


async def rate_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(",", ".")
    try:
        rate = float(text)
        if rate < 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Введите корректную ставку (0 или больше). Пример: 15.5")
        return RATE

    amount = context.user_data["amount"]
    months = context.user_data["months"]

    try:
        monthly_payment, total_payment, overpayment = calc_annuity_payment(amount, months, rate)
    except ValueError as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
        return AMOUNT  # Начать заново с суммы

    await update.message.reply_text(
        "✅ Результаты расчёта:\n\n"
        f"💰 Сумма кредита: {amount:,.2f} ₽\n"
        f"📅 Срок: {months} месяцев\n"
        f"📊 Ставка: {rate:.2f} % годовых\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 Ежемесячный платёж: {monthly_payment:,.2f} ₽\n"
        f"💵 Общая выплата: {total_payment:,.2f} ₽\n"
        f"📉 Переплата: {overpayment:,.2f} ₽\n\n"
        "🎯 Хотите посчитать ещё раз?\n"
        "Введите новую сумму или /cancel для выхода:"
    )
    return AMOUNT  # 🔄 Возврат на ввод суммы — бесконечный цикл!


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Диалог завершён.\n"
        "Отправьте /start для нового расчёта!"
    )
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler)],
            MONTHS: [MessageHandler(filters.TEXT & ~filters.COMMAND, months_handler)],
            RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, rate_handler)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()


    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
