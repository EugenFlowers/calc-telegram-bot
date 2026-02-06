import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ Добавьте BOT_TOKEN в Bothost.ru")
    exit(1)

# Этапы анкеты
Q1_CREDIT_HISTORY, Q2_INCOME, Q3_DEBTS, Q4_AGE, Q5_PURPOSE = range(5)


async def global_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Глобальный /start — всегда работает и сбрасывает анкету."""
    context.user_data.clear()
    keyboard = [
        [InlineKeyboardButton("Хорошая ✅", callback_data="q1_good")],
        [InlineKeyboardButton("Средняя ⚠️", callback_data="q1_medium")],
        [InlineKeyboardButton("Плохая ❌", callback_data="q1_bad")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📋 Анкета кредитной истории\n\n"
        "❓ Вопрос 1/5:\n"
        "<b>Какая у вас кредитная история?</b>\n\n"
        "• Хорошая: своевременные платежи\n"
        "• Средняя: 1-2 просрочки\n"
        "• Плохая: много просрочек/суды",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return Q1_CREDIT_HISTORY


async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    stage = context.user_data.get("stage", 0)
    
    # Сохраняем ответ
    context.user_data[f"q{stage+1}"] = data

    stage += 1
    context.user_data["stage"] = stage

    if stage == 5:
        # Финальный расчёт
        await show_result(query, context.user_data)
        return

    # Следующий вопрос
    await show_next_question(query, stage)


async def show_next_question(query, stage: int):
    texts = {
        1: "❓ Вопрос 2/5:\n<b>Какой у вас ежемесячный доход?</b>\n\n• >100к ₽\n• 50-100к ₽\n• <50к ₽",
        2: "❓ Вопрос 3/5:\n<b>Есть ли текущие долги?</b>\n\n• Нет\n• Есть, но погашаю\n• Много долгов",
        3: "❓ Вопрос 4/5:\n<b>Ваш возраст?</b>\n\n• 25-35 лет\n• 36-50 лет\n• >50 лет",
        4: "❓ Вопрос 5/5:\n<b>Цель кредита?</b>\n\n• Покупка авто\n• Ремонт/товары\n• Бизнес/инвестиции"
    }
    
    keyboards = {
        1: [[InlineKeyboardButton(">100к", callback_data="q2_high"), InlineKeyboardButton("50-100к", callback_data="q2_med")], [InlineKeyboardButton("<50к", callback_data="q2_low")]],
        2: [[InlineKeyboardButton("Нет ✅", callback_data="q3_no"), InlineKeyboardButton("Есть, погашаю", callback_data="q3_yes_pay")], [InlineKeyboardButton("Много", callback_data="q3_many")]],
        3: [[InlineKeyboardButton("25-35", callback_data="q4_young"), InlineKeyboardButton("36-50", callback_data="q4_mid")], [InlineKeyboardButton(">50", callback_data="q4_old")]],
        4: [[InlineKeyboardButton("Авто", callback_data="q5_car"), InlineKeyboardButton("Ремонт/товары", callback_data="q5_goods")], [InlineKeyboardButton("Бизнес", callback_data="q5_bus")]]
    }

    text = texts.get(stage, "Ошибка")
    keyboard = keyboards.get(stage, [[InlineKeyboardButton("Назад", callback_data="back")]])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="HTML")


async def show_result(query, user_data):
    # Подсчёт баллов (упрощённая логика)
    score = 0
    reasons = []

    # Q1 Кредитная история
    if user_data.get("q1") == "q1_good": score += 30
    elif user_data.get("q1") == "q1_medium": score += 10; reasons.append("Средняя кредитная история")
    else: score += 0; reasons.append("Плохая кредитная история")

    # Q2 Доход
    if user_data.get("q2") == "q2_high": score += 25
    elif user_data.get("q2") == "q2_med": score += 15
    else: score += 5; reasons.append("Низкий доход")

    # Q3 Долги
    if user_data.get("q3") == "q3_no": score += 20
    elif user_data.get("q3") == "q3_yes_pay": score += 10
    else: score += 0; reasons.append("Много текущих долгов")

    # Q4 Возраст
    if user_data.get("q4") == "q4_young": score += 15
    elif user_data.get("q4") == "q4_mid": score += 10
    else: score += 5

    # Q5 Цель
    if user_data.get("q5") == "q5_car": score += 10
    elif user_data.get("q5") == "q5_goods": score += 5
    else: score += 15  # Бизнес лучше воспринимается

    # Результат
    if score >= 80:
        result = "🎉 ОТЛИЧНЫЙ! Одобрение 95%+"
        advice = "Вам одобрят любой кредит под минимальную ставку!"
    elif score >= 60:
        result = "✅ ХОРОШО! Одобрение 70-90%"
        advice = "Хорошие шансы. Улучшите кредитную историю."
    elif score >= 40:
        result = "⚠️ СРЕДНЕ! Одобрение 30-60%"
        advice = "Возможен небольшой кредит. Погасите долги."
    else:
        result = "❌ НИЗКИЙ! Одобрение <20%"
        advice = "Сначала исправьте кредитную историю и долги."

    keyboard = [[InlineKeyboardButton("🔄 Новый опрос", callback_data="restart")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"<b>{result}</b>\n\n"
        f"Ваш балл: <b>{score}/100</b>\n\n"
        f"📊 Проблемы:\n• {' | '.join(reasons) if reasons else 'Нет'}\n\n"
        f"💡 Рекомендации:\n{advice}\n\n"
        f"🔄 /start — новая анкета",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await global_start(update, context)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", global_start), group=-1)  # Всегда первый
    
    app.add_handler(CallbackQueryHandler(handle_question))
    app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))

    app.run_polling()


if __name__ == "__main__":
    main()



