# -*- coding: utf-8 -*-

import telebot
from telebot import types
import json

# ====== НАСТРОЙКА ======
TOKEN = "8587332178:AAHRQB_jlmSSNca0UC401CMqMWvvKMAdWtM"

ADMIN_IDS = [7729088553,1059193183,680379633]

bot = telebot.TeleBot(TOKEN, threaded=False)

user_data = {}

# ====== ҚОЛДАНУШЫЛАРДЫ САҚТАУ ======
def save_user(user):
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
    except:
        users = {}

    users[str(user.id)] = {
        "username": user.username,
        "first_name": user.first_name
    }

    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# ====== START ======
@bot.message_handler(commands=['start'])
def start(message):

    save_user(message.from_user)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💌 Аноним хабарлама жіберу")

    bot.send_message(
        message.chat.id,
        "👋 Сәлем!\n\n"
        "Бұл бот арқылы психологқа аноним түрде хабарлама жібере аласыз.",
        reply_markup=markup
    )

# ====== ХАБАРЛАМА БАСТАУ ======
@bot.message_handler(func=lambda message: message.text == "💌 Аноним хабарлама жіберу")
def ask_class(message):

    msg = bot.send_message(
        message.chat.id,
        "📚 Сыныбыңызды жазыңыз:\n\nМысалы: 9А"
    )

    bot.register_next_step_handler(msg, ask_gender)

# ====== ЖЫНЫС ======
def ask_gender(message):

    user_data[message.chat.id] = {}
    user_data[message.chat.id]["class"] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👦 Ер", "👧 Әйел")

    msg = bot.send_message(
        message.chat.id,
        "👤 Жынысыңызды таңдаңыз:",
        reply_markup=markup
    )

    bot.register_next_step_handler(msg, get_message)

# ====== МӘСЕЛЕ ======
def get_message(message):

    user_data[message.chat.id]["gender"] = message.text

    msg = bot.send_message(
        message.chat.id,
        "✍️ Хабарламаңызды жазыңыз:",
        reply_markup=types.ReplyKeyboardRemove()
    )

    bot.register_next_step_handler(msg, send_to_admin)

# ====== АДМИНГЕ ЖІБЕРУ ======
def send_to_admin(message):

    data = user_data.get(message.chat.id, {})

    user_id = message.from_user.id

    save_user(message.from_user)

    text = (
        "📩 ЖАҢА АНОНИМ ХАБАРЛАМА\n\n"
        f"🆔 ID: {user_id}\n"
        f"📚 Сынып: {data.get('class')}\n"
        f"👤 Жыныс: {data.get('gender')}\n\n"
        f"💬 Хабарлама:\n{message.text}"
    )

    for admin in ADMIN_IDS:
        try:
            bot.send_message(admin, text)
        except Exception as e:
            print("Админге жіберу қатесі:", e)

    bot.send_message(
        message.chat.id,
        "✅ Хабарламаңыз психологқа жіберілді!"
    )

# ====== REPLY ======
@bot.message_handler(commands=['reply'])
def reply(message):

    if message.from_user.id not in ADMIN_IDS:
        return

    args = message.text.split(" ", 2)

    if len(args) < 3:
        bot.send_message(
            message.chat.id,
            "❌ Формат дұрыс емес!\n\n"
            "/reply ID мәтін"
        )
        return

    try:
        user_id = int(args[1])

        reply_text = args[2]

        bot.send_message(
            user_id,
            f"💬 Психолог жауабы:\n\n{reply_text}"
        )

        bot.send_message(
            message.chat.id,
            "✅ Жауап жіберілді!"
        )

    except Exception as e:

        bot.send_message(
            message.chat.id,
            f"❌ Қате:\n{e}"
        )

# ====== USERS ======
@bot.message_handler(commands=['users'])
def users_list(message):

    if message.from_user.id not in ADMIN_IDS:
        return

    try:
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)

        text = "👥 Қолданушылар тізімі:\n\n"

        for uid, info in users.items():
            text += (
                f"ID: {uid}\n"
                f"Username: @{info.get('username')}\n"
                f"Аты: {info.get('first_name')}\n\n"
            )

        bot.send_message(message.chat.id, text)

    except:
        bot.send_message(message.chat.id, "❌ Қолданушылар табылмады.")

# ====== ІСКЕ ҚОСУ ======
print("Бот іске қосылды...")

bot.polling(none_stop=True, skip_pending=True)
