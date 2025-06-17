import logging
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Персонажи с характеристиками
CHARACTERS = {
    "player": {
        "health": 100,
        "inventory": [],
        "damage": (10, 20),
        "defense": 5,
    },
    "dragon": {
        "health": 180,
        "damage": (20, 35),
        "defense": 12,
    },
    "snake": {
        "health": 70,
        "damage": (10, 18),
        "defense": 4,
    },
    "goblin": {
        "health": 90,
        "damage": (8, 20),
        "defense": 5,
    },
    "shadow_wraith": {
        "health": 120,
        "damage": (18, 30),
        "defense": 10,
    }
}

# Локации и квесты с расширенными сюжетными элементами и интерактивностью
QUESTS = {
    "castle": {
        "name": "Квест: Тайны древнего замка",
        "start_step": "start",
        "steps": {
            "start": {
                "text": "Вы стоите перед величественным замком, покрытым древними рунами. Легенды гласят, что внутри спрятаны артефакты, способные изменить судьбу мира. Что вы сделаете?",
                "options": [
                    "➡️ Войти через главные ворота",
                    "⬅️ Обойти замок в поисках тайного прохода",
                    "🔥 Вызвать древнего духа на помощь",
                    "🔙 Прервать квест и вернуться в меню"
                ],
            },
            "🔥 Вызвать древнего духа на помощь": {
                "text": "Вы напеваете древний заклинательный гимн. Из тумана выходит дух. Он обещает помощь, но просит взамен частицу вашей силы.",
                "options": [
                    "Отдать часть здоровья духу",
                    "Отказать и продолжить самостоятельно",
                    "🔙 Прервать квест и вернуться в меню"
                ],
                "effect_choices": {
                    "Отдать часть здоровья духу": {"health": -30, "damage_bonus": 15},
                    "Отказать и продолжить самостоятельно": {}
                }
            },
            "Отдать часть здоровья духу": {
                "text": "Дух принял вашу жертву. Ваш урон значительно увеличен. Будьте осторожны с силой.",
                "options": [
                    "➡️ Войти через главные ворота",
                    "⬅️ Обойти замок в поисках тайного прохода",
                    "🔙 Прервать квест и вернуться в меню"
                ],
            },
            "Отказать и продолжить самостоятельно": {
                "text": "Без помощи духа путь будет труднее, но вы полны решимости.",
                "options": [
                    "➡️ Войти через главные ворота",
                    "⬅️ Обойти замок в поисках тайного прохода",
                    "🔙 Прервать квест и вернуться в меню"
                ],
            },
            "➡️ Войти через главные ворота": {
                "text": "Внутри вы видите роскошный зал, в центре которого стоит загадочный алтарь. Внезапно появляется охранник – тень, которая вызывает вас на бой!",
                "options": ["⚔️ Сразиться с тенью", "🏃‍♂️ Попытаться спрятаться", "🔙 Прервать квест и вернуться в меню"],
                "battle": "shadow_wraith"
            },
            "⬅️ Обойти замок в поисках тайного прохода": {
                "text": "Вы находите скрытую дверь, покрытую паутиной древних времён. Открыть её?",
                "options": ["🔓 Открыть дверь", "↩️ Вернуться к входу", "🔙 Прервать квест и вернуться в меню"],
            },
            "🔓 Открыть дверь": {
                "text": "За дверью глубокий подземный тоннель. Видны три направления: светлый коридор, темный проход и лестница вниз.",
                "options": ["➡️ Светлый коридор", "🌑 Темный проход", "⬇️ Лестница вниз", "🔙 Прервать квест и вернуться в меню"]
            },
            "➡️ Светлый коридор": {
                "text": "Коридор ведёт к древней библиотеке. Здесь хранится книга заклинаний.",
                "options": ["📖 Взять книгу заклинаний", "↩️ Вернуться в тоннель", "🔙 Прервать квест и вернуться в меню"],
            },
            "📖 Взять книгу заклинаний": {
                "text": "Книга дала вам магические знания, ваш урон и защита увеличены.",
                "options": ["↩️ Вернуться в тоннель", "🔙 Прервать квест и вернуться в меню"],
                "effect": {"damage_bonus": 10, "defense_bonus": 10, "items": ["Книга заклинаний"]},
            },
            "🌑 Темный проход": {
                "text": "В темноте вас атакуют гоблины!",
                "options": ["⚔️ Сразиться", "🏃‍♂️ Убежать"],
                "battle": "goblin"
            },
            "⬇️ Лестница вниз": {
                "text": "Лестница ведет в подземелье, где скрывается дракон, охраняющий великий артефакт.",
                "options": ["⚔️ Сразиться с драконом", "↩️ Вернуться в тоннель", "🔙 Прервать квест и вернуться в меню"],
                "battle": "dragon"
            },
            "🏃‍♂️ Попытаться спрятаться": {
                "text": "Тень заметила вас и нанесла внезапный удар. Вы потеряли часть здоровья.",
                "options": ["⚔️ Сразиться", "🏃‍♂️ Убежать", "🔙 Прервать квест и вернуться в меню"],
                "effect": {"health": -20},
            },
            "⚔️ Сразиться с тенью": {
                "text": "Битва с тенью начинается!",
                "options": ["Атаковать", "Защититься", "Попытаться убежать"],
                "battle": "shadow_wraith"
            },
            "⚔️ Сразиться": {
                "text": "Битва началась!",
                "options": ["Атаковать", "Защититься", "Попытаться убежать"],
            },
            "🏃‍♂️ Убежать": {
                "text": "Вы с трудом спаслись, потеряв здоровье.",
                "options": ["🔄 Начать заново", "🔙 Прервать квест и вернуться в меню"],
                "effect": {"health": -30}
            },
            "🔄 Начать заново": {
                "text": "Вы у входа в замок. Что дальше?",
                "options": [
                    "➡️ Войти через главные ворота",
                    "⬅️ Обойти замок в поисках тайного прохода",
                    "🔥 Вызвать древнего духа на помощь",
                    "🔙 Прервать квест и вернуться в меню"
                ],
            },
        },
    },
    "cave": {
        "name": "Квест: Загадки тёмной пещеры",
        "start_step": "start",
        "steps": {
            "start": {
                "text": "Вы подходите к темному входу в пещеру. Легенды гласят, что в ней спрятан свиток мудрости. Какие действия вы предпримете?",
                "options": [
                    "➡️ Войти в пещеру",
                    "🔦 Включить факел",
                    "⬅️ Отойти назад",
                    "🔙 Прервать квест и вернуться в меню"
                ],
            },
            "🔦 Включить факел": {
                "text": "С включенным факелом вы видите темные тени, движущиеся в глубинах пещеры.",
                "options": [
                    "➡️ Войти в пещеру",
                    "👂 Прислушаться к звукам",
                    "🔙 Прервать квест и вернуться в меню"
                ],
                "effect": {"damage_bonus": 5}
            },
            "➡️ Войти в пещеру": {
                "text": "Глубже в пещере вы видите три прохода: левый с шелестом листвы, правый с холодным воздухом и центральный с мерцанием.",
                "options": [
                    "🍃 Левый проход",
                    "❄️ Правый проход",
                    "✨ Центральный проход",
                    "🔙 Прервать квест и вернуться в меню"
                ],
            },
            "🍃 Левый проход": {
                "text": "Вы попадаете в подземный сад с магическими цветами. Вы находите таинственный цветок, который может исцелять.",
                "options": ["Взять цветок", "Исследовать дальше", "↩️ Вернуться к развилке", "🔙 Прервать квест и вернуться в меню"],
            },
            "Взять цветок": {
                "text": "Цветок добавлен в ваш инвентарь и восстанавливает 40 здоровья при использовании.",
                "options": ["Исследовать дальше", "↩️ Вернуться к развилке", "🔙 Прервать квест и вернуться в меню"],
                "effect": {"items": ["Лечебный цветок"]},
            },
            "Исследовать дальше": {
                "text": "Вы натыкаетесь на гоблина. Он пытается вас ограбить.",
                "options": ["⚔️ Сразиться", "🏃‍♂️ Убежать"],
                "battle": "goblin",
            },
            "❄️ Правый проход": {
                "text": "Проход ведет к ледяной комнате, где охраняет змей ледяной дракон.",
                "options": ["⚔️ Сразиться с ледяным драконом", "↩️ Вернуться к развилке", "🔙 Прервать квест и вернуться в меню"],
                "battle": "dragon",  # Можно расширить, чтобы был ледяной дракон отдельно
            },
            "✨ Центральный проход": {
                "text": "Вы находите древний алтарь с рунами. Вы чувствуете могущественную энергию. Попытаться активировать алтарь?",
                "options": [
                    "✅ Активировать алтарь",
                    "❌ Игнорировать и пойти обратно",
                    "🔙 Прервать квест и вернуться в меню"
                ],
            },
            "✅ Активировать алтарь": {
                "text": "Алтарь дарует вам магическую щитовую ауру! Защита увеличена на 20.",
                "options": ["↩️ Вернуться к развилке", "🔙 Прервать квест и вернуться в меню"],
                "effect": {"defense_bonus": 20},
            },
            "❌ Игнорировать и пойти обратно": {
                "text": "Вы решили не рисковать. Возвращаетесь назад.",
                "options": ["↩️ Вернуться к развилке", "🔙 Прервать квест и вернуться в меню"],
            },
            "⬅️ Отойти назад": {
                "text": "Вы решаете вернуться домой, не рискуя.",
                "options": ["🔄 Начать заново", "🔙 Прервать квест и вернуться в меню"],
            },
            "🔄 Начать заново": {
                "text": "Вы у входа в пещеру. Что дальше?",
                "options": [
                    "➡️ Войти в пещеру",
                    "🔦 Включить факел",
                    "⬅️ Отойти назад",
                    "🔙 Прервать квест и вернуться в меню"
                ],
            },
        },
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    user_data.clear()
    user_data["health"] = CHARACTERS["player"]["health"]
    user_data["inventory"] = []
    user_data["damage_bonus"] = 0
    user_data["defense_bonus"] = 0

    keyboard = [[quest["name"]] for quest in QUESTS.values()]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "Привет! Выберите квест, чтобы начать:",
        reply_markup=reply_markup,
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_data = context.user_data

    if text == "🔙 Прервать квест и вернуться в меню":
        user_data.clear()
        await start(update, context)
        return

    if "current_quest" not in user_data:
        for key, quest in QUESTS.items():
            if text == quest["name"]:
                user_data["current_quest"] = key
                user_data["current_step"] = quest["start_step"]
                await send_quest_step(update, user_data)
                return

        for quest in QUESTS.values():
            step = quest["steps"].get("start")
            if step and "effect_choices" in step and text in step["effect_choices"]:
                user_data["current_quest"] = "castle"
                eff = step["effect_choices"][text]
                if "health" in eff:
                    user_data["health"] = max(1, user_data.get("health", 100) + eff["health"])
                if "damage_bonus" in eff:
                    user_data["damage_bonus"] = user_data.get("damage_bonus", 0) + eff["damage_bonus"]
                user_data["current_step"] = text
                await update.message.reply_text(f"Эффект применен. Здоровье: {user_data['health']}, Урон бонус: {user_data.get('damage_bonus', 0)}")
                await send_quest_step(update, user_data)
                return

        await update.message.reply_text("Пожалуйста, выберите квест, используя кнопки ниже.")
        return

    current_quest = user_data["current_quest"]
    current_step_key = user_data.get("current_step")
    quest = QUESTS[current_quest]
    steps = quest["steps"]

    if current_step_key is None or current_step_key not in steps:
        await update.message.reply_text("Ошибка состояния. Начинаем заново.")
        user_data.clear()
        await start(update, context)
        return

    options = steps[current_step_key]["options"]
    if text not in options:
        await update.message.reply_text("Пожалуйста, используйте кнопки для выбора варианта.")
        return

    step = steps[current_step_key]

    user_data["current_step"] = text

    if "effect" in step:
        effect = step["effect"]
        if "health" in effect:
            user_data["health"] += effect["health"]
            if user_data["health"] > 100:
                user_data["health"] = 100
            elif user_data["health"] <= 0:
                await update.message.reply_text("Вы погибли. Квест завершён.")
                user_data.clear()
                await start(update, context)
                return
            await update.message.reply_text(f"Ваше здоровье теперь {user_data['health']}.")
        if "damage_bonus" in effect:
            user_data["damage_bonus"] = user_data.get("damage_bonus", 0) + effect["damage_bonus"]
            await update.message.reply_text(f"Ваш урон увеличен на {effect['damage_bonus']}.")
        if "defense_bonus" in effect:
            user_data["defense_bonus"] = user_data.get("defense_bonus", 0) + effect["defense_bonus"]
            await update.message.reply_text(f"Ваша защита увеличена на {effect['defense_bonus']}.")
        if "items" in effect:
            user_data.setdefault("inventory", [])
            for item in effect["items"]:
                if item not in user_data["inventory"]:
                    user_data["inventory"].append(item)
            await update.message.reply_text(f"В инвентарь добавлены предметы: {', '.join(effect['items'])}.")
        if "remove_items" in effect:
            for item in effect["remove_items"]:
                if item in user_data.get("inventory", []):
                    user_data["inventory"].remove(item)
            await update.message.reply_text(f"Из инвентаря удалены предметы: {', '.join(effect['remove_items'])}.")

    if "requires_item" in step:
        required = step["requires_item"]
        if required not in user_data.get("inventory", []):
            await update.message.reply_text(f"Для этого действия требуется предмет: {required}. Выберите другой вариант.")
            user_data["current_step"] = current_step_key
            return

    if "battle" in step:
        battle_enemy_key = step["battle"]
        if battle_enemy_key in CHARACTERS:
            battle_result = await battle(update, user_data, battle_enemy_key)
            if not battle_result:
                await update.message.reply_text("Вы проиграли в битве. Квест завершён.")
                user_data.clear()
                await start(update, context)
                return
            else:
                user_data["current_step"] = "🔄 Начать заново"
                await update.message.reply_text("Вы выиграли битву! Продолжаем приключение.")
                await send_quest_step(update, user_data)
                return

    if text == "🔄 Начать заново":
        user_data["current_step"] = quest["start_step"]
        user_data["health"] = CHARACTERS["player"]["health"]
        user_data["damage_bonus"] = 0
        user_data["defense_bonus"] = 0
        user_data["inventory"] = []

    await send_quest_step(update, user_data)

async def send_quest_step(update: Update, user_data: dict) -> None:
    current_quest = user_data["current_quest"]
    current_step_key = user_data["current_step"]
    quest = QUESTS[current_quest]
    step = quest["steps"].get(current_step_key)

    if step is None:
        await update.message.reply_text("Ошибка: Шаг не найден.")
        return

    text = step["text"]
    options = step["options"]
    keyboard = [[option] for option in options]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    health = user_data.get("health", 100)
    inventory = user_data.get("inventory", [])
    status = f"❤️ Здоровье: {health} | 🎒 Инвентарь: {', '.join(inventory) if inventory else 'пусто'}"
    await update.message.reply_text(status)
    await update.message.reply_text(text=text, reply_markup=reply_markup)

async def battle(update: Update, user_data: dict, enemy_key: str) -> bool:
    enemy = CHARACTERS[enemy_key].copy()
    player = {
        "health": user_data.get("health", 100),
        "damage_min": CHARACTERS["player"]["damage"][0] + user_data.get("damage_bonus", 0),
        "damage_max": CHARACTERS["player"]["damage"][1] + user_data.get("damage_bonus", 0),
        "defense": CHARACTERS["player"]["defense"] + user_data.get("defense_bonus", 0),
    }
    enemy_health = enemy["health"]
    enemy_defense = enemy["defense"]

    await update.message.reply_text(f"Битва началась с {enemy_key.capitalize()}!")

    while player["health"] > 0 and enemy_health > 0:
        player_damage = random.randint(player["damage_min"], player["damage_max"]) - enemy_defense
        player_damage = max(0, player_damage)
        enemy_health -= player_damage
        await update.message.reply_text(f"Вы нанесли урон {player_damage} врагу. Здоровье врага: {max(enemy_health, 0)}")

        if enemy_health <= 0:
            break

        enemy_damage = random.randint(enemy["damage"][0], enemy["damage"][1]) - player["defense"]
        enemy_damage = max(0, enemy_damage)
        player["health"] -= enemy_damage
        await update.message.reply_text(f"Враг нанёс урон {enemy_damage}. Ваше здоровье: {max(player['health'], 0)}")

    user_data["health"] = max(player["health"], 0)

    return user_data["health"] > 0

def main() -> None:
    TOKEN = "7567135692:AAGERrXNJ2-02yZwG4zo0g0i5i7DSoTYHz0"

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()

