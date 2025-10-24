from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from django.conf import settings
from habits.models import Profile
from asgiref.sync import sync_to_async

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    username = update.message.from_user.username

    # ORM вызов в асинхронном контексте
    profile, created = await sync_to_async(Profile.objects.get_or_create)(user=None)
    profile.telegram_chat_id = chat_id
    await sync_to_async(profile.save)()

    await context.bot.send_message(chat_id=chat_id, text="Привет! Теперь я буду напоминать тебе о привычках.")

def run_bot():
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
