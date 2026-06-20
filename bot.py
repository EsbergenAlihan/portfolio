import sys
import re
import os
from telebot import TeleBot, types
from content import PORTFOLIO_CONTENT

def parse_args():
    args = sys.argv[1:]
    token = None
    debug = False

    i = 0
    while i < len(args):
        if args[i] == '--token' and i + 1 < len(args):
            token = args[i + 1]
            i += 2
        elif args[i] == '--debug':
            debug = True
            i += 1
        else:
            i += 1

    if not token:
        token = os.getenv('BOT_TOKEN')

    return token, debug


TOKEN, DEBUG = parse_args()

if not TOKEN:
    print("❌ Ошибка: укажи токен через --token или переменную окружения BOT_TOKEN")
    sys.exit(1)

bot = TeleBot(TOKEN)


def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton("👤 О себе", callback_data='about'),
        types.InlineKeyboardButton("🎯 Моя цель", callback_data='goal'),
        types.InlineKeyboardButton("🚀 Как я пришёл в IT", callback_data='story'),
        types.InlineKeyboardButton("👨‍🏫 Мой ментор", callback_data='mentor'),
        types.InlineKeyboardButton("📈 Точка А → Б", callback_data='progress'),
        types.InlineKeyboardButton("🎮 Хобби", callback_data='hobbies'),
        types.InlineKeyboardButton("💼 Мои работы", callback_data='works'),
        types.InlineKeyboardButton("🐙 GitHub", callback_data='github'),
    ]
    markup.add(*buttons)
    return markup


def back_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("◀️ Назад в меню", callback_data='menu'))
    return markup


@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    try:
        text = (
            f"Привет, {message.from_user.first_name}! 👋\n\n"
            "Это моё портфолио «Обо мне». Выбери раздел:"
        )
        bot.send_message(message.chat.id, text, reply_markup=main_menu())
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] Ошибка в start: {e}")


@bot.message_handler(commands=['about', 'goal', 'story', 'mentor', 'progress', 'hobbies', 'works', 'github'])
def send_section(message):
    try:
        cmd = message.text.lstrip('/')
        content = PORTFOLIO_CONTENT.get(cmd, "Раздел в разработке.")
        bot.send_message(
            message.chat.id,
            content,
            reply_markup=back_button(),
            parse_mode='HTML',
            disable_web_page_preview=False
        )
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] Ошибка в команде {message.text}: {e}")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        data = call.data
        if data == 'menu':
            bot.edit_message_text(
                "Главное меню. Выбери раздел:",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=main_menu()
            )
            return

        content = PORTFOLIO_CONTENT.get(data, "Раздел в разработке.")
        bot.edit_message_text(
            content,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back_button(),
            parse_mode='HTML',
            disable_web_page_preview=False
        )
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] Ошибка в callback: {e}")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        text = message.text

        question_pattern = re.compile(
            r'^(что|как|почему|зачем|кто|где|когда|какой|чей|сколько)\b|.*\?$',
            re.IGNORECASE
        )

        if question_pattern.search(text):
            answer = (
                "Это хороший вопрос! 🤖\n\n"
                "Я пока учусь отвечать на свободные вопросы, "
                "но всё о себе рассказываю через меню ниже:"
            )
        else:
            answer = (
                "Я тебя не совсем понял 🤷‍♂️\n\n"
                "Воспользуйся меню или командами:\n"
                "/about, /goal, /story, /mentor, /progress, /hobbies, /works, /github"
            )

        bot.send_message(message.chat.id, answer, reply_markup=main_menu())
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] Ошибка в handle_text: {e}")

if __name__ == '__main__':
    print("🚀 Бот запущен!")
    if DEBUG:
        print("[DEBUG] Режим отладки включён")
    bot.polling(none_stop=True)