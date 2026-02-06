# Анкета кредитной истории — Telegram-бот

## Запуск локально

1. Создать `.env`:
   BOT_TOKEN=токен_от_BotFather
2. Установить зависимости:
   pip install -r requirements.txt
3. Запустить:
   python bot.py

## Деплой на Bothost.ru

1. Создать репозиторий на GitHub с файлами:
   - bot.py
   - requirements.txt
   - Dockerfile
2. В Bothost:
   - Создать нового бота
   - Указать ссылку на GitHub
   - В «Переменные окружения» добавить:
     BOT_TOKEN=токен_от_BotFather
3. Собрать и запустить.

Команда `/start` запускает анкету заново.

