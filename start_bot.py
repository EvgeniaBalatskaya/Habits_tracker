import os
import django

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from habits.bot_handler import run_bot

if __name__ == "__main__":
    run_bot()
