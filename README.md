# Habits Tracker

Приложение на Django с Telegram-ботом для отслеживания привычек.

## Описание проекта

- Пользователь может создавать полезные и приятные привычки.
- Можно ставить вознаграждения или связывать привычки.
- Telegram-бот управляет привычками через команды.
- Поддержка публичных привычек, видимых другим пользователям.
- Напоминания о привычках через Telegram.
- Контроль времени выполнения привычки и периодичности.
- Пагинация списка привычек по 5 на страницу.
- Отложенные задачи через Celery для напоминаний.

## Функционал бота

- `/start` — регистрация и приветствие пользователя.
- `/add_habit <действие> <время> <место> <длительность_сек> <публичная(True/False)> [reward/related_id]` — создать привычку.
- `/my_habits` — показать текущие привычки пользователя (до 5 на страницу).
- `/done <habit_id>` — отметить привычку выполненной и получить вознаграждение.
- `/public_habits` — показать публичные привычки других пользователей.

### Пример команды:

/add_habit "Прогулка" "19:00" "Парк" 120 True "Десерт"


## Установка

1. Клонировать репозиторий:

git clone https://github.com/EvgeniaBalatskaya/Habits_tracker.git
cd habits_tracker
python -m venv .venv
.venv\Scripts\activate     # Windows

Создать и активировать виртуальное окружение:

# или source .venv/bin/activate  # Linux/Mac

Установить зависимости:

pip install -r requirements.txt

Настроить переменные окружения .env:

DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
SECRET_KEY=your_django_secret
TELEGRAM_BOT_TOKEN=your_bot_token

Применить миграции:

python manage.py migrate

Запустить бота:

python start_bot.py

##Технологии

Python 3.13

Django 5.x

PostgreSQL/SQLite

Telegram Bot API

Celery для отложенных задач

Flake8 для проверки стиля кода


