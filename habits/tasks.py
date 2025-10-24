from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import Habit
from telegram import Bot
from datetime import datetime

@shared_task
def send_habit_reminders():
    """
    Проходим по привычкам и отправляем напоминания, если пришло время.
    Простая стратегия:
     - для каждой привычки: если today matches schedule (periodicity) AND time_of_day ~ сейчас => отправить.
    В реальном проекте лучше организовать сообщения по таймзоне пользователя.
    """
    now = timezone.localtime()
    today = now.date()
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    # todo: оптимизировать выборкой только тех, у кого should_remind_today == True
    habits = Habit.objects.select_related("owner").all()
    for h in habits:
        # пропускаем приватные, если у пользователя не указан chat_id — нужно хранить chat_id у пользователя
        # Предполагаем: у user.profile.telegram_chat_id хранится chat id (или поле в модели User)
        user = h.owner
        chat_id = getattr(user, "telegram_chat_id", None)
        if not chat_id:
            continue

        # 1) проверить периодичность (should_remind_today)
        if not h.should_remind_today(today):
            continue

        # 2) проверить время: если часы и минуты совпадают (можно допускать +/- 5 минут)
        habit_time = datetime.combine(today, h.time_of_day)
        diff = abs((timezone.localtime() - timezone.make_aware(habit_time)).total_seconds())
        if diff <= 300:  # 5 минут
            text = f"Напоминание: {h.action} в {h.place or '...'} — {h.estimated_seconds} сек. Reward: {h.reward or '—'}"
            try:
                bot.send_message(chat_id=chat_id, text=text)
            except Exception as e:
                # логирование ошибки
                print("Telegram send error:", e)
