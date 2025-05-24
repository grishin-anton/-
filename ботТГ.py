import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Определяем квесты с шагами: каждый квест - это словарь шагов, текст шага и варианты ответов
QUESTS = {
    "castle": {
        "name": "Квест: Замок",
        "start_step": "start",
        "steps": {
            "start": {
                "text": "Вы у входа в таинственный замок. Что вы сделаете?",
                "options": ["➡️ Войти внутрь", "⬅️ Обойти вокруг", "🔙 Прервать квест и вернуться в меню"],
            },
            "➡️ Войти внутрь": {
                "text": "Вы вошли и видите лестницу и дверь. Куда пойдёте?",
                "options": ["⬆️ Подняться по лестнице", "🚪 Открыть дверь", "🔙 Прервать квест и вернуться в меню"],
            },
            "⬅️ Обойти вокруг": {
                "text": "Обойдя замок, нашли потайной проход. Войти?",
                "options": ["🚶‍♂️ Войти в проход", "↩️ Вернуться к входу", "🔙 Прервать квест и вернуться в меню"],
            },
            "⬆️ Подняться по лестнице": {
                "text": "Там дракон! Что делать?",
                "options": ["⚔️ Сразиться с драконом", "🏃‍♂️ Бежать вниз", "🔙 Прервать квест и вернуться в меню"],
            },
            "🚪 Открыть дверь": {
                "text": "Сундук с сокровищами! Квест завершён! Поздравляем 🎉",
                "options": ["🔄 Начать заново", "🔙 Прервать квест и вернуться в меню"],
            },
            "🚶‍♂️ Войти в проход": {
                "text": "Темно, вы нашли тайную комнату с книгой.",
                "options": ["📖 Взять книгу", "↩️ Выйти обратно", "🔙 Прервать квест и вернуться в меню"],
            },
            "⚔️ Сразиться с драконом": {
                "text": "Вы победили дракона! Квест завершён! 🏆",
                "options": ["🔄 Начать заново", "🔙 Прервать квест и вернуться в меню"],
            },
            "📖 Взять книгу": {
                "text": "Книга волшебная! Вы маг. Квест завершён! ✨",
                "options": ["🔄 Начать заново", "🔙 Прервать квест и вернуться в меню"],
            },
            "🏃‍♂️ Бежать вниз": {
                "text": "Вернулись к входу в замок.",
                "options": ["➡️ Войти внутрь", "⬅️ Обойти вокруг", "🔙 Прервать квест и вернуться в меню"],
            },
            "↩️ Вернуться к входу": {
                "text": "Вы у входа в замок.",
                "options": ["➡️ Войти внутрь", "⬅️ Обойти вокруг", "🔙 Прервать квест и вернуться в меню"],
            },
            "↩️ Выйти обратно": {
                "text": "Вы у входа в замок.",
                "options": ["➡️ Войти внутрь", "⬅️ Обойти вокруг", "🔙 Прервать квест и вернуться в меню"],
            },
            "🔄 Начать заново": {
                "text": "Вы у входа в замок. Что дальше?",
                "options": ["➡️ Войти внутрь", "⬅️ Обойти вокруг", "🔙 Прервать квест и вернуться в меню"],
            },
        },
    },
    "cave": {
        "name": "Квест: Пещера",
        "start_step": "start",
        "steps": {
            "start": {
                "text": "Вы стоите у входа в темную пещеру. Что вы сделаете?",
                "options": ["➡️ Войти в пещеру", "⬅️ Отойти назад", "🔙 Прервать квест и вернуться в меню"],
            },
            "➡️ Войти в пещеру": {
                "text": "Внутри слышны странные звуки и виднеется светлый проход. Куда пойдёте?",
                "options": ["➡️ Идти на свет", "👂 Исследовать звук", "🔙 Прервать квест и вернуться в меню"],
            },
            "⬅️ Отойти назад": {
                "text": "Вы решили безопасно уйти домой. Квест завершён.",
                "options": ["🔄 Начать заново", "🔙 Прервать квест и вернуться в меню"],
            },
            "➡️ Идти на свет": {
                "text": "Вы вышли в красивый подземный сад, полный сияющих цветов. Квест завершён! 🌸",
                "options": ["🔄 Начать заново", "🔙 Прервать квест и вернуться в меню"],
            },
            "👂 Исследовать звук": {
                "text": "Звук оказался шипением змеи! Что делать?",
                "options": ["⚔️ Сразиться", "🏃‍♂️ Убежать", "🔙 Прервать квест и вернуться в меню"],
            },
            "⚔️ Сразиться": {
                "text": "Вы победили змею! Герой! Квест завершён! 🏆",
                "options": ["🔄 Начать заново", "🔙 Прервать квест и вернуться в меню"],
            },
            "🏃‍♂️ Убежать": {
                "text": "Вы убежали из пещеры, спасаясь от опасности.",
                "options": ["🔄 Начать заново", "🔙 Прервать квест и вернуться в меню"],
            },
            "🔄 Начать заново": {
                "text": "Вы у входа в пещеру. Что дальше?",
                "options": ["➡️ Войти в пещеру", "⬅️ Отойти назад", "🔙 Прервать квест и вернуться в меню"],
            },
        },
    },
}

# Показывает главное меню с квестами для выбора
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Создаём клавиатуру с кнопками для выбора квеста
    keyboard = [[quest["name"]] for quest in QUESTS.values()]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Привет! Выберите квест, чтобы начать:",
        reply_markup=reply_markup,
    )
    context.user_data.clear()  # Очищаем данные пользователя

# Обрабатывает выбор пользователя из меню квестов или шагов квеста
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text  # Получаем текст сообщения от пользователя
    user_data = context.user_data  # Получаем данные пользователя 

    # Проверяем, если пользователь хочет прервать квест и вернуться в меню
    if text == "🔙 Прервать квест и вернуться в меню":
        user_data.clear()
        await start(update, context)
        return

    # Если квест ещё не выбран, проверяем, выбрал ли пользователь квест из меню
    if "current_quest" not in user_data:
        # Пытаемся найти квест по имени
        for key, quest in QUESTS.items():
            if text == quest["name"]:
                user_data["current_quest"] = key  # Сохраняем выбранный квест
                user_data["current_step"] = quest["start_step"]  # Устанавливаем начальный шаг
                await send_quest_step(update, user_data)  # Отправляем шаг квеста
                return
        # Если текст не распознан, просим выбрать квест
        await update.message.reply_text(
            "Пожалуйста, выберите квест, используя кнопки ниже.",
        )
        return

    # Если квест уже выбран, обрабатываем выбор шагов квеста
    current_quest = user_data["current_quest"]
    current_step_key = user_data.get("current_step")
    quest = QUESTS[current_quest]
    steps = quest["steps"]

    # Проверяем, является ли ответ пользователя допустимым вариантом на текущем шаге
    if current_step_key is None or current_step_key not in steps:
        # Если состояние некорректно, сбрасываем квест
        await update.message.reply_text(
            "Ошибка состояния. Начинаем заново.",
        )
        user_data.clear()  # Очищаем данные пользователя
        await start(update, context)  # Запускаем меню заново
        return

    options = steps[current_step_key]["options"]
    if text not in options:
        # Если выбран недопустимый вариант
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки для выбора варианта.",
        )
        return

    # Обновляем текущий шаг
    user_data["current_step"] = text

    # Если шаг текста "Начать заново", сбрасываем шаг квеста на начальный
    if text == "🔄 Начать заново":
        user_data["current_step"] = quest["start_step"]

    await send_quest_step(update, user_data)  # Отправляем следующий шаг квеста

# Отправляет сообщение с текстом шага и показывает всплывающую клавиатуру с вариантами
async def send_quest_step(update: Update, user_data: dict) -> None:
    current_quest = user_data["current_quest"]
    current_step_key = user_data["current_step"]
    quest = QUESTS[current_quest]
    steps = quest["steps"]
    step = steps.get(current_step_key)

    if step is None:
        await update.message.reply_text("Ошибка: Шаг не найден.")
        return

    text = step["text"]
    options = step["options"]
    keyboard = [[option] for option in options]  # Формируем клавиатуру с вариантами
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(text=text, reply_markup=reply_markup)  # Отправляем сообщение с шагом

def main() -> None:
    TOKEN = "7567135692:AAGERrXNJ2-02yZwG4zo0g0i5i7DSoTYHz0"  # Токен бота

    application = ApplicationBuilder().token(TOKEN).build()  # Создаём приложение бота

    application.add_handler(CommandHandler("start", start))  # Обработчик команды /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # Обработчик текстовых сообщений

    print("Bot is running...")  # Сообщение о запуске бота
    application.run_polling()  # Запускаем бота

if __name__ == '__main__':
    main()  # Запускаем основную функцию при запуске скрипта

