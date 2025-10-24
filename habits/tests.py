import pytest
from django.core.exceptions import ValidationError
from habits.models import Habit
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from django.conf import settings
from habits.models import Profile
from celery import shared_task
from telegram import Bot
from django.conf import settings
from habits.models import Profile

User = get_user_model()

@pytest.mark.django_db
def test_habit_validators():
    user = User.objects.create_user(username="u", password="p")
    pleasant = Habit.objects.create(owner=user, action="Чаёвничать", time_of_day="09:00", is_pleasant=True)
    # приятная не должна иметь reward
    with pytest.raises(ValidationError):
        h = Habit(owner=user, action="A", time_of_day="10:00", is_pleasant=True, reward="Cake")
        h.full_clean()
    # related must be pleasant
    h2 = Habit(owner=user, action="B", time_of_day="10:00", is_pleasant=False)
    h2.save()
    with pytest.raises(ValidationError):
        h3 = Habit(owner=user, action="C", time_of_day="10:00", related_habit=h2)
        h3.full_clean()

@pytest.mark.django_db
def test_habit_crud_api():
    u = User.objects.create_user(username="a", password="p")
    client = APIClient()
    client.force_authenticate(user=u)
    data = {"action":"Run", "time_of_day":"07:00", "estimated_seconds":60}
    resp = client.post("/api/habits/", data)
    assert resp.status_code == 201
    # list
    resp2 = client.get("/api/habits/")
    assert resp2.status_code == 200
    assert resp2.json()["count"] == 1


def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    username = update.message.from_user.username

    # Найдём пользователя по username
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        # Если пользователя нет, можно создать
        profile = Profile.objects.create(user=None, telegram_chat_id=chat_id)

    # Сохраняем chat_id
    profile.telegram_chat_id = chat_id
    profile.save()

    # Отправляем ответ
    context.bot.send_message(chat_id=chat_id, text="Привет! Теперь я буду напоминать тебе о привычках.")

@shared_task
def send_habit_reminders():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    profiles = Profile.objects.exclude(telegram_chat_id__isnull=True)

    for profile in profiles:
        chat_id = profile.telegram_chat_id
        bot.send_message(chat_id=chat_id, text="Напоминание: пора выполнить привычку!")