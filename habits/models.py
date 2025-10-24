from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    action = models.CharField(max_length=255)  # Действие
    time = models.TimeField()                  # Время выполнения
    place = models.CharField(max_length=255)   # Место
    is_pleasant = models.BooleanField(default=False)  # Признак приятной привычки
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'is_pleasant': True},  # Только приятные привычки
        related_name="main_habits"
    )
    reward = models.CharField(max_length=255, blank=True, null=True)
    frequency_days = models.PositiveIntegerField(default=1)  # Периодичность в днях
    duration_seconds = models.PositiveIntegerField(default=60)  # Время на выполнение
    is_public = models.BooleanField(default=False)  # Публичная привычка

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Валидаторы

        # Приятная привычка не может иметь reward или related_habit
        if self.is_pleasant:
            if self.reward or self.related_habit:
                raise ValidationError("У приятной привычки не может быть вознаграждения или связанной привычки")

        # Одновременно reward и related_habit быть не могут
        if self.reward and self.related_habit:
            raise ValidationError("Можно указать либо вознаграждение, либо связанную привычку, но не оба сразу")

        # Время на выполнение <= 120 секунд
        if self.duration_seconds > 120:
            raise ValidationError("Время выполнения не должно превышать 120 секунд")

        # Периодичность >= 1 день и <= 7 дней
        if self.frequency_days < 1 or self.frequency_days > 7:
            raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней")


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def should_remind_today(self, date=None):
        """
        Простая логика: напомнить, если с last_performed >= periodicity_days или last_performed is None.
        For scheduling we'll check dates and times in celery task.
        """
        date = date or timezone.now().date()
        if self.last_performed is None:
            return True
        delta = date - self.last_performed
        return delta.days >= self.periodicity_days


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username