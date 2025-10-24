from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models

class Habit(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="habits")
    place = models.CharField(max_length=255, blank=True)
    time_of_day = models.TimeField()  # время выполнения
    action = models.CharField(max_length=255)
    is_pleasant = models.BooleanField(default=False)  # признак приятной привычки
    related_habit = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name="linked_to")
    periodicity_days = models.PositiveIntegerField(default=1)  # периодичность в днях, по умолчанию 1
    reward = models.CharField(max_length=255, blank=True)  # текст вознаграждения
    estimated_seconds = models.PositiveIntegerField(default=120)  # время на выполнение в секундах
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # optional: store last_performed date for scheduling logic
    last_performed = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        # 1. нельзя одновременно указать reward и related_habit (в полезной привычке)
        if self.reward and self.related_habit:
            raise ValidationError("Нельзя одновременно указывать вознаграждение и связанную привычку.")

        # 2. estimated_seconds <= 120
        if self.estimated_seconds > 120:
            raise ValidationError("Время выполнения не должно превышать 120 секунд.")

        # 3. в связанные привычки могут попадать только привычки с is_pleasant=True
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна быть признаком приятной привычки.")

        # 4. у приятной привычки не может быть reward или related_habit
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError("У приятной привычки не должно быть вознаграждения или связанной привычки.")

        # 5. нельзя выполнять реже, чем раз в 7 дней: periodicity_days <= 7
        if self.periodicity_days > 7:
            raise ValidationError("Нельзя устанавливать периодичность более 7 дней.")

        # 6. also: periodicity_days >= 1
        if self.periodicity_days < 1:
            raise ValidationError("Периодичность должна быть не менее 1 дня.")

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_chat_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username