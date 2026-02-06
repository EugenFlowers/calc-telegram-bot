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

# Вопросы анкеты (простая линейная логика)
QUESTIONS = {
    1: {
        "text": (
            "📋 Анкета кредитной истории\n\n"
            "❓ Вопрос 1/3:\n"
            "<b>Какая у вас кредитная история?</b>"
        ),
        "buttons": [
            [InlineKeyboardButton("Хорошая ✅", callback_data="q1_good")],
            [InlineKeyboardButton("Средняя ⚠️", callback_data="q1_medium")],
            [InlineKeyboardButton("Плохая ❌", callback_data="q1_bad")],
        ],
    },
    2: {
        "text": (
            "❓ Вопрос 2/3:\n"
            "<b>Есть ли текущие просрочки по кредитам?</b>"
        ),
        "buttons": [
            [InlineKeyboardButton("Нет ✅", callback_data="q2_no")],
            [InlineKeyboardButton("Редко", callback_data="q2_some")],
            [InlineKeyboardButton("Часто ❌", callback_data="q2_many")],
        ],
    },
    3: {
        "text": (
            "❓ Вопрос 3/3:\n"
            "<b>Какой у вас примерный ежемесячный доход?</b>"
        ),
        "buttons": [
            [InlineKeyboardButton("> 100 000 ₽", callback_data="q3_high")],
            [InlineKeyboardButton("50–100 000 ₽", callback_data="q3_mid")],
            [InlineKeyboardButton("< 50 000 ₽", callback_data="q3_low")],
        ],
    },
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Всегда запускает анкету с первого вопроса."""
    context.user_data.clear()
    context.user_data["step"] = 1
    await send_question(update, context, step=1)


async def send_question(update_or_query, context: ContextTypes.DEFAULT_TYPE, step: int):
    """Отправка/обновление сообщения с вопросом."""
    q = QUESTIONS[step]
    markup = InlineKeyboardMarkup(q["buttons"])

    # Если это первое сообщение — reply_text
    if isinstance(update_or_query, Update) and update_or_query.message:
        await update_or_query.message.reply_text(
            q["text"], reply_markup=markup, parse_mode="HTML"
        )
    else:
        query = update_or_query
        await query.edit_message_text(
            q["text"], reply_markup=markup, parse_mode="HTML"
        )


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Единственный обработчик ВСЕХ кнопок — работает с первого клика."""
    query = update.callback_query
    await query.answer()  # обязательно

    data = query.data

    # Перезапуск с кнопки
    if data == "restart":
        context.user_data.clear()
        context.user_data["step"] = 1
        await send_question(query, context, step=1)
        return

    # Текущий шаг
    step = context.user_data.get("step", 1)

    # Сохраняем ответ (если нужно — можно логировать в БД)
    context.user_data[f"answer_{step}"] = data

    # Если ещё есть вопросы — идём дальше
    if step < 3:
        step += 1
        context.user_data["step"] = step
        await send_question(query, context, step=step)
        return

    # Если это был последний вопрос — показываем результат
    await show_result(query, context)


async def show_result(query, context: ContextTypes.DEFAULT_TYPE):
    """Простейшая оценка по ответам."""
    a1 = context.user_data.get("answer_1")
    a2 = context.user_data.get("answer_2")
    a3 = context.user_data.get("answer_3")

    score = 0

    # История
    if a1 == "q1_good":
        score += 40
    elif a1 == "q1_medium":
        score += 20
    else:
        score += 5

    # Просрочки
    if a2 == "q2_no":
        score += 30
    elif a2 == "q2_some":
        score += 10
    else:
        score += 0

    # Доход
    if a3 == "q3_high":
        score += 30
    elif a3 == "q3_mid":
        score += 15
    else:
        score += 5

    if score >= 80:
        text = (
            "🎉 <b>Отличная кредитная анкета!</b>\n\n"
            f"Ваш условный рейтинг: <b>{score}/100</b>\n\n"
            "Шансы на одобрение высокого кредита — очень высокие."
        )
    elif score >= 50:
        text = (
            "✅ <b>Неплохо!</b>\n\n"
            f"Ваш условный рейтинг: <b>{score}/100</b>\n\n"
            "Шансы на одобрение есть, но условия могут быть средними."
        )
    else:
        text = (
            "⚠️ <b>Слабая анкета.</b>\n\n"
            f"Ваш условный рейтинг: <b>{score}/100</b>\n\n"
            "Нужно улучшать историю и снижать просрочки."
        )

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔄 Пройти ещё раз", callback_data="restart")]]
    )

    await query.edit_message_text(
        text + "\n\nКоманда /start тоже перезапускает анкету.",
        reply_markup=markup,
        parse_mode="HTML",
    )


def main():
    app = Application.builder().token(TOKEN).build()

    # /start всегда срабатывает и показывает первый экран
    app.add_handler(CommandHandler("start", start))

    # Один обработчик для ВСЕХ inline‑кнопок
   
