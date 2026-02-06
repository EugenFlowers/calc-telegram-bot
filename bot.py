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


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ЕДИНСТВЕННЫЙ обработчик — ВСЕ кнопки работают с 1 клика!"""
    query = update.callback_query
    await query.answer()  # Обязательно! Убирает "часики"

    data = query.data

    # Перезапуск анкеты
    if data == "restart":
        context.user_data.clear()
        await global_start(query, context)
        return

    # Сохраняем этап
    stage = context.user_data.get("stage", 0)
    context.user_data[f"q{stage+1}"] = data
    context.user_data["stage"] = stage + 1

    stage += 1

    # Последний вопрос — показываем результат
    if stage == 5:
        await show_result(query, context.user_data)
        return

    # Показываем следующий вопрос
    await show_question(query, stage)


async def show_question(query, stage: int):
    """Показывает вопрос по номеру этапа."""
    questions = {
        1: ("Вопрос 2/5:\n<b>Какой у вас ежемесячный дохо



if __name__ == "__main__":
    main()



