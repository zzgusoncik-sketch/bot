from telebot import TeleBot, types
import re, json, os, time, random

BOT_TOKEN = "8444926066:AAFxz7bI7ZTPikyKBXJlKG0ys4SnRo6jg3w"
bot = TeleBot(BOT_TOKEN)

# Список админов (замени на реальные Telegram ID админов)
ADMIN_IDS = [1511040538]

# === Загрузка пользователей ===
if os.path.exists("users.json"):
    with open("users.json", "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = {}

# === Сохранение пользователей ===
def save_users():
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# === Главное меню с фото ===
def open_menu_direct(message):
    markup = types.InlineKeyboardMarkup()
    rob_btn = types.InlineKeyboardButton("💣 Ограбить банк", callback_data="rob_bank")
    balance_btn = types.InlineKeyboardButton("💰 Проверить баланс", callback_data="check_balance")
    daily_btn = types.InlineKeyboardButton("🎰 Ежедневный прокрут", callback_data="daily_spin")
    markup.add(rob_btn)
    markup.add(balance_btn)
    markup.add(daily_btn)

    bot.send_photo(
        message.chat.id,
        photo="https://i.postimg.cc/SXcpK7XN/Spin-Menu.png",
        caption="🏠 Главное меню:\n",
        reply_markup=markup
    )

# === /start ===
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)

    # Обновление старых пользователей
    if user_id in users and isinstance(users[user_id], str):
        users[user_id] = {
            "nickname": users[user_id],
            "balance": 0,
            "last_rob": 0,
            "last_spin": 0
        }
        save_users()

    # Инициализация ключей для старых пользователей
    if user_id in users:
        if "balance" not in users[user_id]:
            users[user_id]["balance"] = 0
        if "last_rob" not in users[user_id]:
            users[user_id]["last_rob"] = 0
        if "last_spin" not in users[user_id]:
            users[user_id]["last_spin"] = 0
        save_users()
        open_menu_direct(message)
    else:
        bot.send_message(
            message.chat.id,
            "👋 Привет!\nЧтобы зарегистрироваться, напиши свой ник Telegram "
            "(только латиница, цифры и нижнее подчёркивание):\n\nПример: @MrXg1rcio"
        )
        bot.register_next_step_handler(message, register_username)

# === Регистрация пользователя ===
def register_username(message):
    user_id = str(message.from_user.id)
    nickname = message.text.strip()

    if not re.fullmatch(r'@?[A-Za-z0-9_]+', nickname):
        bot.send_message(
            message.chat.id,
            "❌ Некорректный ник!\nИспользуй только латиницу, цифры и _.\nПопробуй снова:"
        )
        bot.register_next_step_handler(message, register_username)
        return

    if nickname.startswith("@"):
        nickname = nickname[1:]

    users[user_id] = {
        "nickname": nickname,
        "balance": 0,
        "last_rob": 0,
        "last_spin": 0
    }
    save_users()

    markup = types.InlineKeyboardMarkup()
    menu_btn = types.InlineKeyboardButton("🏠 Перейти в меню", callback_data="open_menu")
    markup.add(menu_btn)

    bot.send_message(
        message.chat.id,
        f"✅ Вы успешно авторизовались (@{nickname})",
        reply_markup=markup
    )

# === Обработка кнопок ===
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)

    # Защита от незарегистрированных
    if user_id not in users:
        bot.answer_callback_query(call.id, "❌ Сначала зарегистрируйтесь через /start")
        return

    # Инициализация ключей на случай старых пользователей
    if "balance" not in users[user_id]:
        users[user_id]["balance"] = 0
    if "last_rob" not in users[user_id]:
        users[user_id]["last_rob"] = 0
    if "last_spin" not in users[user_id]:
        users[user_id]["last_spin"] = 0
    save_users()

    # --- Меню ---
    if call.data == "open_menu":
        open_menu_direct(call.message)

# --- Проверка баланса ---
    elif call.data == "check_balance":
        balance = users[user_id]["balance"]
        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("🏠 Перейти в меню", callback_data="open_menu")
        markup.add(back_btn)

        bot.send_photo(
            call.message.chat.id,
            photo="https://i.postimg.cc/qhgXLQ2L/Balance.png",
            caption=f"💰 Ваш баланс: {balance} JoJo\n\nВы можете пополнить его, написав администратору @MrXg1rcik",
            reply_markup=markup
        )

    # --- Ограбление банка ---
    elif call.data == "rob_bank":
        now = time.time()
        last_rob = users[user_id]["last_rob"]
        diff = now - last_rob

        if diff < 86400:
            hours = int((86400 - diff) // 3600)
            bot.answer_callback_query(call.id, f"⏳ Вы уже грабили! Попробуйте через {hours} ч.")
            return

        success = random.randint(1, 100) <= 30
        if success:
            users[user_id]["balance"] += 300
            text = "💸 Вы успешно ограбили банк и получили 300 JoJo!"
        else:
            text = "🚨 Вас поймали! Следующая попытка через 24 часа."

        users[user_id]["last_rob"] = now
        save_users()

        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("🏠 Перейти в меню", callback_data="open_menu")
        markup.add(back_btn)

        bot.send_photo(
            call.message.chat.id,
            photo="https://i.postimg.cc/vgP28cvT/Bank-Rob.png",
            caption=text,
            reply_markup=markup
        )

    # --- Ежедневный прокрут ---
    elif call.data == "daily_spin":
        now = time.time()
        last_spin = users[user_id].get("last_spin", 0)
        diff = now - last_spin

        if diff < 86400:
            hours = int((86400 - diff) // 3600)
            bot.answer_callback_query(call.id, f"⏳ Ежедневный прокрут уже был! Попробуйте через {hours} ч.")
            return

        # Шансы для каждого числа
        rewards = [20, 40, 80, 160]
        chances = [50, 30, 15, 5]
        roll = random.randint(1, 100)
        cumulative = 0
        for reward, chance in zip(rewards, chances):
            cumulative += chance
            if roll <= cumulative:
                gained = reward
                break

        users[user_id]["balance"] += gained
        users[user_id]["last_spin"] = now
        save_users()

        markup = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton("🏠 Перейти в меню", callback_data="open_menu")
        markup.add(back_btn)

        # Картинки для разных выпадений
        if gained == 20:
            photo_url = "https://i.postimg.cc/jwsd0k8K/Spin-20.png"
        elif gained == 40:
            photo_url = "https://i.postimg.cc/N2KtQhm2/Spin-40.png"
        elif gained == 80:
            photo_url = "https://i.postimg.cc/G96wv5kc/Spin-80.png"
        elif gained == 160:
            photo_url = "https://i.postimg.cc/GTyfMbk3/Spin-160.png"
        else:
            photo_url = None

        if photo_url:
            bot.send_photo(
                call.message.chat.id,
                photo=photo_url,
                caption=f"🎰 Вы сделали ежедневный прокрут и получили {gained} JoJo!",
                reply_markup=markup
            )
        else:
            bot.send_message(
                call.message.chat.id,
                f"🎰 Вы сделали ежедневный прокрут и получили {gained} JoJo!",
                reply_markup=markup
            )

# === Админские команды: /add и /remove ===
# Формат: /add <user_id> <amount>
#         /remove <user_id> <amount>
def is_admin(message):
    try:
        return int(message.from_user.id) in ADMIN_IDS
    except:
        return False

@bot.message_handler(commands=['add'])
def admin_add(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ У вас нет прав администратора.")
        return

parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "⚠️ Использование: /add <user_id> <amount>")
        return

    target_id, amount_str = parts[1], parts[2]
    if not amount_str.lstrip('-').isdigit():
        bot.reply_to(message, "⚠️ Сумма должна быть целым числом.")
        return

    amount = int(amount_str)
    target_key = str(target_id)

    if target_key not in users:
        bot.reply_to(message, f"⚠️ Пользователь с ID {target_id} не найден в базе.")
        return

    users[target_key]["balance"] = users[target_key].get("balance", 0) + amount
    save_users()

    bot.reply_to(message, f"✅ Начислено {amount} JoJo пользователю ID {target_id}. Текущий баланс: {users[target_key]['balance']} JoJo")

    # Попытка уведомить пользователя (если бот может писать ему)
    try:
        bot.send_message(int(target_id), f"🟢 Вам начислено {amount} JoJo админом. Текущий баланс: {users[target_key]['balance']} JoJo")
    except:
        pass

@bot.message_handler(commands=['remove'])
def admin_remove(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ У вас нет прав администратора.")
        return

    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "⚠️ Использование: /remove <user_id> <amount>")
        return

    target_id, amount_str = parts[1], parts[2]
    if not amount_str.lstrip('-').isdigit():
        bot.reply_to(message, "⚠️ Сумма должна быть целым числом.")
        return

    amount = int(amount_str)
    if amount < 0:
        bot.reply_to(message, "⚠️ Сумма должна быть положительной.")
        return

    target_key = str(target_id)

    if target_key not in users:
        bot.reply_to(message, f"⚠️ Пользователь с ID {target_id} не найден в базе.")
        return

    current = users[target_key].get("balance", 0)
    if current < amount:
        bot.reply_to(message, f"⚠️ У пользователя недостаточно средств. Текущий баланс: {current} JoJo.")
        return

    users[target_key]["balance"] = current - amount
    save_users()

    bot.reply_to(message, f"✅ Списано {amount} JoJo с пользователя ID {target_id}. Текущий баланс: {users[target_key]['balance']} JoJo")

    # Попытка уведомить пользователя (если бот может писать ему)
    try:
        bot.send_message(int(target_id), f"🔴 С вашего баланса списано {amount} JoJo админом. Текущий баланс: {users[target_key]['balance']} JoJo")
    except:
        pass

# === /list ===
@bot.message_handler(commands=['list'])
def list_users(message):
    if not users:
        bot.send_message(message.chat.id, "Пока никто не зарегистрировался 😅")
        return

    text = "📜 Зарегистрированные пользователи:\n\n"
    for uid, data in users.items():
        text += f"@{data['nickname']} — ID: {uid} — 💰 {data.get('balance',0)} JoJo\n"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# === Запуск бота ===
print("🤖 Bot starting...")
bot.polling(none_stop=True)
