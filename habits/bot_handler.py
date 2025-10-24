from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from django.conf import settings
from habits.models import Profile, Habit
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

# ---------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------

async def get_or_create_user_profile(update: Update):
    username = update.message.from_user.username
    chat_id = update.message.chat.id

    user, _ = await sync_to_async(User.objects.get_or_create)(username=username)
    profile, _ = await sync_to_async(Profile.objects.get_or_create)(user=user)
    profile.telegram_chat_id = chat_id
    await sync_to_async(profile.save)()
    return user, profile, chat_id

def format_habit(habit: Habit):
    """Красивый вывод привычки"""
    reward_or_related = habit.reward if habit.reward else (habit.related_habit.action if habit.related_habit else "—")
    return f"{habit.id}: {habit.action} в {habit.time} ({habit.place}), reward: {reward_or_related}"


# ---------- КОМАНДЫ БОТА ----------

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, profile, chat_id = await get_or_create_user_profile(update)
    text = (
        "Привет! Теперь я буду напоминать тебе о привычках.\n\n"
        "Доступные команды:\n"
        "/add_habit — добавить новую привычку\n"
        "/my_habits — показать ваши привычки\n"
        "/done <id> — отметить привычку выполненной\n"
        "/public_habits — показать публичные привычки"
    )
    await context.bot.send_message(chat_id=chat_id, text=text)

# /add_habit
async def add_habit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id

    if not context.args:
        await update.message.reply_text(
            "Чтобы добавить привычку, используйте следующую команду:\n"
            "/add_habit <действие> <время> <место> <длительность_сек> <публичная(Да/Нет)>\n\n"
            "Пример:\n"
            "/add_habit Прогулка 19:00 Парк 120 Да \n"
            "или\n"
            "/add_habit Медитация 07:00 Квартира 60 Нет"
        )
        return

    try:
        args = context.args
        if len(args) < 5:
            raise ValueError("Недостаточно аргументов.")

        action = args[0]
        time_str = args[1]
        place = args[2]
        duration = int(args[3])
        is_public = args[4].lower() == "true"

        reward = None
        related_habit = None
        if len(args) > 5:
            if args[5].isdigit():
                related_habit = await sync_to_async(Habit.objects.get)(id=int(args[5]))
                if not related_habit.is_pleasant:
                    await update.message.reply_text("Связанная привычка должна быть приятной!")
                    return
            else:
                reward = args[5]

        if duration > 120:
            await update.message.reply_text("Время выполнения не должно превышать 120 секунд!")
            return

        user, _, _ = await get_or_create_user_profile(update)

        habit = Habit(
            user=user,
            action=action,
            time=time_str,
            place=place,
            duration_seconds=duration,
            is_public=is_public,
            reward=reward,
            related_habit=related_habit,
            is_pleasant=False
        )
        await sync_to_async(habit.save)()
        await update.message.reply_text(f"Привычка '{action}' успешно добавлена!")
    except Exception as e:
        await update.message.reply_text(
            f"Ошибка: {e}\nИспользуйте:\n"
            "/add_habit <действие> <время> <место> <длительность_сек> <публичная(True/False)> [reward или related_id]"
        )

# /my_habits
async def my_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, _, chat_id = await get_or_create_user_profile(update)
    habits = await sync_to_async(list)(Habit.objects.filter(user=user)[:5])
    if not habits:
        await update.message.reply_text("У вас пока нет привычек.")
        return
    msg = "\n".join([format_habit(h) for h in habits])
    await update.message.reply_text(msg)

# /done <habit_id>
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        habit_id = int(context.args[0])
        user, _, chat_id = await get_or_create_user_profile(update)
        habit = await sync_to_async(Habit.objects.get)(id=habit_id, user=user)

        reward_text = habit.reward or (habit.related_habit.action if habit.related_habit else "—")
        await update.message.reply_text(f"Привычка '{habit.action}' выполнена! Получите награду: {reward_text}")
    except Exception:
        await update.message.reply_text("Ошибка. Используйте: /done <id_привычки>")

# /public_habits
async def public_habits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    habits = await sync_to_async(list)(Habit.objects.filter(is_public=True)[:5])
    if not habits:
        await update.message.reply_text("Публичных привычек пока нет.")
        return
    msg = "\n".join([format_habit(h) for h in habits])
    await update.message.reply_text(msg)


# ---------- ЗАПУСК БОТА ----------

def run_bot():
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_habit", add_habit))
    app.add_handler(CommandHandler("my_habits", my_habits))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(CommandHandler("public_habits", public_habits))
    print("Бот запущен, ожидаю сообщений...")
    app.run_polling()

