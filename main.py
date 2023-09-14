import os
import telebot
import psycopg2
import logging
from lang_pack import *
from config import *
from telebot import types
from flask import Flask, request, render_template

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()
logger = telebot.logger
logger.setLevel(logging.DEBUG)


def who(message):
    db_object.execute(f"SELECT access_level FROM users WHERE id = {message.from_user.id}") # Перевіряєм, чи є користувач в базі
    result = db_object.fetchone()
    if result == None:
        db_object.execute("INSERT INTO users(id, access_level, passed_tests) VALUES (%s, %s, %s)", (message.from_user.id, 0, "#"))
        db_connection.commit()
        return 0
    else:
        return int(result[0]) # Якщо користувач вже відомий, повертається його рівень доступу





@bot.message_handler(commands=["start"])                                                        #/start
def start(message):
    if who(message) == 0: # Звичайний юзер
        user_step_1(message)
    # #db_object.execute(f"SELECT lang FROM users WHERE id = {message.from_user.id}") 
    # result = db_object.fetchone()
    # is_banned_variable = is_banned(message)
    # if is_banned_variable== [False, True]:# Новий і, відповідно, незабанений
    #     db_object.execute("INSERT INTO users(id, currency, lang) VALUES (%s, %s, %s)", (user_id, 0, "UK"))
    #     db_connection.commit()            # Добавляємо його в таблицю
    #     lang_func(message, True)          # Хай вибирає мову
    # elif is_banned_variable == [False, False]:# Не забанений і старий
    #     bot.send_message(message.chat.id, f"{welcome[result[0]]}, {username}!") # Вітаємся
    #     instruction(message, True, False)
    # else:
    #     bot.send_message(message.chat.id, ban[result[0]]) # Хай петляє


def user_step_1(message):
    markup = types.InlineKeyboardMarkup() # Для кнопочок                               # Якщо користувач надумав змінити мову
    new_topic = types.InlineKeyboardButton("Нова тема",  callback_data = "New topic")
    go_over_the_topic = types.InlineKeyboardButton("Перепройти тему",  callback_data = "Go over the topic, 1")
    markup.add(new_topic, go_over_the_topic)                # Тоже для кнопочок
    bot.send_message(message.chat.id, f"Привіт, {message.from_user.username}, бажаємо тобі вдало пройти весь курс, удачі", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def set(call):
    # db_object.execute(f"UPDATE users SET lang = '{call.data[0:2]}' WHERE id = {call.from_user.id}") # Змінюєм мову користувача в базі даних
    # db_connection.commit()
    if call.data[2] == "New topic":
        db_object.execute(f"SELECT passed_tests FROM users WHERE id = {call.message.from_user.id}") # Перевіряєм, чи є користувач в базі
        result = db_object.fetchone()
        if result[0] == "#":
            bot.send_message(call.message.chat.id, f"Так як ти не проходив ще ніяку тему, почнемо з 0")
        else:
            passed_tests = map(int, result[0].split(","))
            for i in range(0, max(passed_tests)):
                if i not in passed_tests:
                    bot.send_message(call.message.chat.id, f"Тема, яку ти ще не проходив - {i}")
        # bot.edit_message_text(f"{welcome[call.data[0:2]]}, {call.data[3:len(list(call.data))]}!", chat_id=call.message.chat.id, message_id=call.message.message_id) # Міняєм просьбу про зміну мови просто на привітання на його мові
        # instruction(call, True, True)
    elif "Go over the topic" in call.data[2]:
        db_object.execute(f"SELECT * FROM admins LIMIT {call.data[2].split(',')[1] * 10}") # Беремо певну кількість тем з БД
        result = db_object.fetchone()
        bot.send_message(call.message.chat.id, result)
        # lang_name = ""
        # if call.data[0:2] == "UK":
        #     lang_name = "English\U0001f1ec\U0001f1e7"
        # if call.data[0:2] == "UA":
        #     lang_name = "Українська\U0001f1fa\U0001f1e6"
        # if call.data[0:2] == "RU":
        #     lang_name = "Русский\U0001f1f7\U0001f1fa"
        # bot.edit_message_text(f"{lang[call.data[0:2]]} {lang_name}", chat_id=call.message.chat.id, message_id=call.message.message_id) # Добавляєм до просьби вибрану ним мову


# @bot.message_handler(commands=["lang"])                                                          #/lang
# def lang_func(message, start = False):
#     if is_banned(message) == [True, False]:
#         db_object.execute(f"SELECT lang FROM users WHERE id = {message.from_user.id}") 
#         result = db_object.fetchone()
#         bot.send_message(message.chat.id, ban[result[0]])
#     else:
#         markup = types.InlineKeyboardMarkup() # Для кнопочок
#         if start:                             # Якщо корристувач тільки що приєднався і оце вибирає мову
#             UK = types.InlineKeyboardButton("English\U0001f1ec\U0001f1e7",  callback_data  = "UKT" + message.from_user.username)
#             UA = types.InlineKeyboardButton("Українська\U0001f1fa\U0001f1e6",  callback_data = "UAT" + message.from_user.username)
#             RU = types.InlineKeyboardButton("Русский\U0001f1f7\U0001f1fa",  callback_data = "RUT" + message.from_user.username)
#         else:                                 # Якщо користувач надумав змінити мову
#             UK = types.InlineKeyboardButton("English\U0001f1ec\U0001f1e7",  callback_data = "UKF")
#             UA = types.InlineKeyboardButton("Українська\U0001f1fa\U0001f1e6",  callback_data = "UAF")
#             RU = types.InlineKeyboardButton("Русский\U0001f1f7\U0001f1fa",  callback_data = "RUF")
#         markup.add(UK, UA, RU)                # Тоже для кнопочок
#         db_object.execute(f"SELECT lang FROM users WHERE id = {message.from_user.id}") 
#         result = db_object.fetchone()

#         if start:                             # Якщо корристувач тільки що приєднався і оце вибирає мову
#             bot.send_message(message.chat.id, f"Hello, {message.from_user.username}! " + lang[result[0]], reply_markup=markup) # Вітаємся на англійській і просим вибрати мову
#         else:
#             bot.send_message(message.chat.id, lang[result[0]], reply_markup=markup) # Просто хай вибирає мову












# @bot.message_handler(commands=["my_money"])                                                       #/my_money
# def my_money(message):
#     if is_banned(message) == [True, False]:
#         db_object.execute(f"SELECT lang FROM users WHERE id = {message.from_user.id}") 
#         result = db_object.fetchone()
#         bot.send_message(message.chat.id, ban[result[0]])
#     else:
#         db_object.execute(f"SELECT currency, lang FROM users WHERE id = {message.from_user.id}") # Знаходим у таблиці кількість кристалів у користувача та його мову
#         result = db_object.fetchall()
#         print(result)
#         bot.send_message(message.chat.id, crystals[result[0][1]].replace("x", str(result[0][0])))








# @bot.message_handler(commands=["help"])                                                           #/help
# def help(message):
#     if is_banned(message) == [True, False]:
#         db_object.execute(f"SELECT lang FROM users WHERE id = {message.from_user.id}") 
#         result = db_object.fetchone()
#         bot.send_message(message.chat.id, ban[result[0]])
#     else:
#         db_object.execute(f"SELECT lang FROM users WHERE id = {message.from_user.id}")
#         result = db_object.fetchone()
#         bot.send_message(message.chat.id, help_lang[result[0]])







# @bot.message_handler(commands=["instruction"])                                                           #/instruction
# def instruction(message, start = False, start1 = False):
#     if is_banned(message) == [True, False]:
#         db_object.execute(f"SELECT lang FROM users WHERE id = {message.from_user.id}") 
#         result = db_object.fetchone()
#         bot.send_message(message.chat.id, ban[result[0]])
#     else:
#         db_object.execute(f"SELECT lang FROM users WHERE id = {message.from_user.id}")
#         result = db_object.fetchone()
#         markup = types.InlineKeyboardMarkup() # Для кнопочок
#         button1 = types.InlineKeyboardButton(instruction_button[result[0]], urls[result[0]])
#         button2 = types.InlineKeyboardButton(trade_button[result[0]], url = "https://steamcommunity.com/login/home/")
#         markup.add(button1, button2)                # Тоже для кнопочок
#         if start == False:
#             bot.send_chat_action(message.chat.id, action='typing')
#             bot.send_message(message.chat.id, instruction_lang[result[0]], reply_markup=markup)
#         else:
#             if start1:
#                 bot.send_chat_action(message.message.chat.id, action='typing')
#                 bot.send_message(message.message.chat.id, trade[result[0]], reply_markup=markup)
#             else:
#                 bot.send_chat_action(message.chat.id, action='typing')
#                 bot.send_message(message.chat.id, trade[result[0]], reply_markup=markup)
            


# @bot.message_handler(content_types=['text'])
# def get_trade(message):
#     if all(message.text != it for it in ["/instruction", "/start", "/lang", "/my_money", "/help"]):
#         db_object.execute(f"SELECT lang FROM users WHERE id = {message.from_user.id}") 
#         result = db_object.fetchone()
#         if is_banned(message) == [True, False]:
#             bot.send_message(message.chat.id, ban[result[0]])
#         else:
#             if len(list(message.text)) > 25 and (message.text[0:25] == "http://steamcommunity.com" or message.text[0:26] == "https://steamcommunity.com"):
#                 bot.send_message(1397377881, "Чел: `" + message.from_user.username + "`\n" + "Мова: " + str(result[0]) + "\n" + "id: `" + str(message.from_user.id) + "`", parse_mode='MarkdownV2') # 
#                 bot.send_message(1397377881, message.text)
#                 bot.send_message(message.chat.id, ok[result[0]])
#             else:
#                 bot.send_message(message.chat.id, invalid_message[result[0]])



@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200







# @server.route('/', methods=['GET', 'POST'])
# def webapp():
#     return render_template("index.html", color='pink')


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))) 
