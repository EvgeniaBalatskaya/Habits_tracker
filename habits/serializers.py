from rest_framework import serializers
from .models import Habit

class HabitSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Habit
        fields = [
            "id", "owner", "place", "time_of_day", "action", "is_pleasant",
            "related_habit", "periodicity_days", "reward", "estimated_seconds",
            "is_public", "created_at", "updated_at", "last_performed"
        ]

    def validate(self, data):
        # owner available at create via request.user
        is_pleasant = data.get("is_pleasant", getattr(self.instance, "is_pleasant", False))
        reward = data.get("reward", getattr(self.instance, "reward", ""))
        related = data.get("related_habit", getattr(self.instance, "related_habit", None))
        est = data.get("estimated_seconds", getattr(self.instance, "estimated_seconds", 120))
        periodicity = data.get("periodicity_days", getattr(self.instance, "periodicity_days", 1))

        # 1. can't have reward and related
        if reward and related:
            raise serializers.ValidationError("Нельзя задавать одновременно вознаграждение и связанную привычку.")

        # 2. est <= 120
        if est > 120:
            raise serializers.ValidationError("Время выполнения не должно превышать 120 секунд.")

        # 3. related must be pleasant
        if related and not related.is_pleasant:
            raise serializers.ValidationError("Связанная привычка должна быть приятной.")

        # 4. pleasant cannot have reward/related
        if is_pleasant and (reward or related):
            raise serializers.ValidationError("У приятной привычки не должно быть вознаграждения или связанной привычки.")

        # 5. periodicity bounds
        if periodicity < 1 or periodicity > 7:
            raise serializers.ValidationError("Периодичность должна быть от 1 до 7 дней.")

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["owner"] = user
        return super().create(validated_data)
