import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Берём токен из переменной окружения
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("❌ Ошибка: не найден BOT_TOKEN в переменных окружения.")
    raise SystemExit(1)


# ====== ЛОГИКА АНКЕТЫ ======

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
            "<b>Есть ли у вас текущие просрочки по кредитам?</b>"
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
            "<b>Какой у вас ежемесячный доход?</b>"
        ),
        "buttons"


   
