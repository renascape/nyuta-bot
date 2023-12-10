import telebot
from telebot import types
import time
import sqlite3
from datetime import datetime
from keys import BOT_TOKEN
from keys import ADMIN_ID

bot = telebot.TeleBot(BOT_TOKEN)

#  Создание базы данных
conn = sqlite3.connect('BotDatabase.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        username TEXT,
        name TEXT NOT NULL,
        level INTEGER DEFAULT 0,
        group_name TEXT NOT NULL,
        regdate TEXT NOT NULL
    );
    """)

conn.commit()
conn.close()


##################
#  Команда /start#
##################
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id

    if str(message.chat.id).startswith('-'):
        bot.reply_to(message, f'Эта команда доступна только в личных сообщениях с ботом!')
    else:
        bot.send_message(user_id, "Привет! Введи свое имя и фамилию чтобы продолжить:\nНапример: Александр Пушкин")
        bot.register_next_step_handler(message, get_group)

def get_group(message):
    user_id = message.from_user.id
    name = message.text
    bot.send_message(user_id, "Теперь введи название своей группы:\nНапример: ИПО-20.24")
    bot.register_next_step_handler(message, lambda message: add_user_to_database(message, user_id, name))


#  Добавление имени фамилии и группы в базу данных
def add_user_to_database(message, user_id, name):
    username = message.from_user.username
    group_name = message.text

    conn = sqlite3.connect('BotDatabase.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()

    if existing_user:
        bot.send_message(user_id, "❌ Кажется, ты уже зарегистрирован в базе данных.")
    else:
        cursor.execute("INSERT INTO users (user_id, name, username, group_name, regdate) VALUES (?, ?, ?, ?, ?)", (user_id, name, username, group_name, datetime.now()))
        conn.commit()

    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIxA2Vwb9u2JFHI9bW118zaFGRALZ0JAAJXEwACsdrYSxCdi3yCDx7WMwQ')
    bot.send_message(user_id, f"🌟Отлично, {message.from_user.first_name}, теперь ты в базе учеников!\nЖми /menu чтобы продолжить. ")

    conn.close()


####################
#  Повышение уровня#
####################
@bot.message_handler(commands=['up'])
def handle_levelup(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIw1mVvnA_YvcCURR31sVtPkI-ASdOJAAJbAgACVp29CgAB3yMzQxabnjME')
        bot.reply_to(message, f"🚫 Похоже, у тебя нет доступа к этой функции!")
    else:
        user_id = message.from_user.id
        up_user_level(user_id)
        bot.reply_to(message, f"✅ Уровень пользователя {message.from_user.first_name} вырос!")

def up_user_level(user_id):
    conn = sqlite3.connect("BotDatabase.db")
    cursor = conn.cursor()

    # Получаем текущий уровень пользователя
    cursor.execute("SELECT level FROM users WHERE user_id= ?", (user_id,))
    result = cursor.fetchone()

    if result:
        current_level = result[0]
        new_level = current_level + 1
        cursor.execute("UPDATE users SET level=? WHERE user_id=?", (new_level, user_id))
    else:
        cursor.execute("INSERT INTO users (user_id, username, level) VALUES (?, ?)", (user_id))

    conn.commit()
    conn.close()

#  Понижение уровня
@bot.message_handler(commands=['down'])
def handle_leveldown(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIw1mVvnA_YvcCURR31sVtPkI-ASdOJAAJbAgACVp29CgAB3yMzQxabnjME')
        bot.reply_to(message, f"🚫 Похоже, у тебя нет доступа к этой функции!")
    else:
        user_id = message.from_user.id
        down_user_level(user_id)
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIxKWVw8tSNd12kPbJj3We7xfljxqeYAAJkAgACVp29CnyLQQ3hCOHMMwQ')
        bot.reply_to(message, f"Уровень пользователя {message.from_user.first_name} понижен!🫤")

def down_user_level(user_id):
    conn = sqlite3.connect("BotDatabase.db")
    cursor = conn.cursor()

    # Получаем текущий уровень пользователя
    cursor.execute("SELECT level FROM users WHERE user_id= ?", (user_id,))
    result = cursor.fetchone()

    if result:
        current_level = result[0]
        new_level = current_level - 1
        cursor.execute("UPDATE users SET level=? WHERE user_id=?", (new_level, user_id))
    else:
        cursor.execute("INSERT INTO users (user_id, username, level) VALUES (?, ?)", (user_id))

    conn.commit()
    conn.close()


################
#  Главное меню#
################
@bot.message_handler(commands=['menu'])
def handle_menu(message):
    if str(message.chat.id).startswith('-'):
        bot.reply_to(message, f'Эта команда доступна только в личных сообщениях с ботом!')
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        button_level = types.KeyboardButton('🏆 Прогресс')
        button_rate = types.KeyboardButton('🎖 Рейтинг')
        button_task = types.KeyboardButton('❗️ Задания')
        button_help = types.KeyboardButton('❓ Помощь')
        button_admin = types.KeyboardButton('🐟 Рыбный отдел')
        markup.add(button_task, button_help, button_level, button_rate, button_admin)
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIvomVpwx6xvVlFfmHcxF85an42HBQCAAJsAgACVp29CioZXpzE0N6fMwQ')
        bot.reply_to(message, f"🔥Привет, {message.from_user.first_name}🔥\nЧем могу помочь?", reply_markup=markup)


##########
# Рейтинг#
##########
@bot.message_handler(func=lambda message: message.text == '🎖 Рейтинг')
def handle_rate(message):
    conn = sqlite3.connect('BotDatabase.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name, username, level FROM users ORDER BY level DESC")
    users = cursor.fetchall()

    rating_message = "Рейтинг пользователей:\n"
    for index, user in enumerate(users, start=1):
        name, username, level = user
        rating_message += f"{index}. {name}({username}) - Ур. {level}\n"

    if rating_message == "Рейтинг пользователей:\n":
        rating_message = "База данных пуста."

    bot.reply_to(message, rating_message)

    conn.close()

@bot.message_handler(func=lambda message: message.text == '🏆 Прогресс')
def handle_level(message):
    user_id = message.from_user.id
    level = get_user_level(user_id)
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIxFmVw1cJE4gJV2HzPIVRiX-5VCXB5AAKFFgAC5n7ZS1CYRw2_NfbiMwQ')
    bot.reply_to(message, f"{message.from_user.first_name} твой текущий уровень: {level}\nТак держать!")


################################
# Получение уровня пользователя#
################################
def get_user_level(user_id):
    conn = sqlite3.connect('BotDatabase.db')
    cursor = conn.cursor()

    cursor.execute("SELECT level FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if result:
        level = result[0]
    else:
        level = 1

    conn.close()
    return level

###########
#  Задания#
###########
@bot.message_handler(func=lambda message: message.text == '❗️ Задания')
def send_task(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(text=TASK_TEXT, url=TASK_LINK)
    markup.add(btn)
    bot.reply_to(message, "📁 Задания:", reply_markup=markup)

#  Методички
@bot.message_handler(func=lambda message: message.text == '❓ Помощь')
def send_task(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(text=HELP_TEXT, url=HELP_LINK)
    markup.add(btn)
    bot.reply_to(message, "📄 Методички:", reply_markup=markup)


############################
#  Рыбный отдел(админ меню)#
############################

@bot.message_handler(func=lambda message: message.text == '🐟 Рыбный отдел')

def admin_level(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIw1mVvnA_YvcCURR31sVtPkI-ASdOJAAJbAgACVp29CgAB3yMzQxabnjME')
        bot.reply_to(message, f"🚫 Похоже, у тебя нет доступа в рыбный отдел!")
    else:
        markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
        button_push = types.KeyboardButton('✉️ Рассылка')
        button_clean = types.KeyboardButton('☠️ Очистка БД')
        button_cleanv = types.KeyboardButton('🗑 Выборочная очистка БД')
        button_linkz = types.KeyboardButton('🔗 Редактировать ссылку заданий')
        button_textz = types.KeyboardButton('✏️ Редактировать текст кнопки заданий')
        button_linkh = types.KeyboardButton('🔗 Редактировать ссылку методичек')
        button_texth = types.KeyboardButton('✏️ Редактировать текст кнопки методичек')
        button_back = types.KeyboardButton('↩️ Вернуться в меню')
        markup.add(button_linkz, button_textz, button_linkh, button_texth, button_push, button_clean, button_cleanv, button_back)
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIw02VvmjfeFNRdZEXEGj7yyvzTkB98AAJoAgACVp29Cl96F8w-AAEUczME')
        bot.reply_to(message, f"🔥Привет, хозяин🔥\nЧем могу быть полезен?", reply_markup=markup)

###############################################################################################################
#  Кнопка возврата из админ меню(по сути это еще одно меню подобное первому лол, переадресация криво работала)#
###############################################################################################################
@bot.message_handler(func=lambda message: message.text == '↩️ Вернуться в меню')
def handle_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    button_level = types.KeyboardButton('🏆 Прогресс')
    button_rate = types.KeyboardButton('🎖 Рейтинг')
    button_task = types.KeyboardButton('❗️ Задания')
    button_help = types.KeyboardButton('❓ Помощь')
    button_admin = types.KeyboardButton('🐟 Рыбный отдел')
    markup.add(button_task, button_help, button_level, button_rate, button_admin)
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIvomVpwx6xvVlFfmHcxF85an42HBQCAAJsAgACVp29CioZXpzE0N6fMwQ')
    bot.reply_to(message, f"🔥Привет, {message.from_user.first_name}🔥\nЧем могу помочь?", reply_markup=markup)


####################################
#  Редактирование ссылки на задания#
####################################
@bot.message_handler(func=lambda message: message.text == '🔗 Редактировать ссылку заданий')
def admin_linkz(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIw1mVvnA_YvcCURR31sVtPkI-ASdOJAAJbAgACVp29CgAB3yMzQxabnjME')
        bot.reply_to(message, f"🚫 Похоже, у тебя нет доступа в рыбный отдел!")
    else:
        bot.reply_to(message, "Введите новую ссылку для заданий:")
        bot.register_next_step_handler(message, update_linkz)

# Проверка на верность введеной ссылки
def update_linkz(message):
    global TASK_LINK
    if message.text.startswith('http'):
        TASK_LINK = message.text
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIxA2Vwb9u2JFHI9bW118zaFGRALZ0JAAJXEwACsdrYSxCdi3yCDx7WMwQ')
        bot.reply_to(message, "✅ Ссылка успешно обновлена.")
    else:
        bot.reply_to(message, "❌ Некорректная ссылка. Введите ссылку, начинающуюся с http://")

#######################################
# Редактирование текста кнопки заданий#
#######################################
@bot.message_handler(func=lambda message: message.text == '✏️ Редактировать текст кнопки заданий')
def admin_textz(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIw1mVvnA_YvcCURR31sVtPkI-ASdOJAAJbAgACVp29CgAB3yMzQxabnjME')
        bot.reply_to(message, f"🚫 Похоже, у тебя нет доступа в рыбный отдел!")
    else:
        bot.reply_to(message, "Введите новый текст для кнопки заданий:")
        bot.register_next_step_handler(message, update_textz)

def update_textz(message):
    global TASK_TEXT
    TASK_TEXT = message.text
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIxA2Vwb9u2JFHI9bW118zaFGRALZ0JAAJXEwACsdrYSxCdi3yCDx7WMwQ')
    bot.reply_to(message, "✅ Текст успешно обновлен.")


######################################
#  Редактирование ссылки на методички#
######################################
@bot.message_handler(func=lambda message: message.text == '🔗 Редактировать ссылку методичек')
def admin_linkh(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIw1mVvnA_YvcCURR31sVtPkI-ASdOJAAJbAgACVp29CgAB3yMzQxabnjME')
        bot.reply_to(message, f"🚫 Похоже, у тебя нет доступа в рыбный отдел!")
    else:
        bot.reply_to(message, "Введите новую ссылку для методичек:")
        bot.register_next_step_handler(message, update_linkh)

#  Проверка верности введеной ссылки
def update_linkh(message):
    global HELP_LINK
    if message.text.startswith('http'):
        HELP_LINK = message.text
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIxA2Vwb9u2JFHI9bW118zaFGRALZ0JAAJXEwACsdrYSxCdi3yCDx7WMwQ')
        bot.reply_to(message, "✅ Ссылка успешно обновлена.")
    else:
        bot.reply_to(message, "❌ Некорректная ссылка. Введите ссылку, начинающуюся с http://")


##########################################
#  Редактирование текста кнопки методичек#
##########################################
@bot.message_handler(func=lambda message: message.text == '✏️ Редактировать текст кнопки методичек')
def admin_texth(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIw1mVvnA_YvcCURR31sVtPkI-ASdOJAAJbAgACVp29CgAB3yMzQxabnjME')
        bot.reply_to(message, f"🚫 Похоже, у тебя нет доступа в рыбный отдел!")
    else:
        bot.reply_to(message, "Введите новый текст для кнопки методичек:")
        bot.register_next_step_handler(message, update_texth)

def update_texth(message):
    global HELP_TEXT
    HELP_TEXT = message.text
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIxA2Vwb9u2JFHI9bW118zaFGRALZ0JAAJXEwACsdrYSxCdi3yCDx7WMwQ')
    bot.reply_to(message, "✅ Текст успешно обновлен.")


###########
# Рассылка#
###########
@bot.message_handler(func=lambda message: message.text == '✉️ Рассылка')
def handle_push(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIw1mVvnA_YvcCURR31sVtPkI-ASdOJAAJbAgACVp29CgAB3yMzQxabnjME')
        bot.reply_to(message, f"🚫 Похоже, у тебя нет доступа в рыбный отдел!")
    else:
        bot.reply_to(message, "Введите текст для рассылки:")
        bot.register_next_step_handler(message, send_message_to_all)

# Отправка сообщения пользователям из базы данных
def send_message_to_all(message):
    conn = sqlite3.connect('BotDatabase.db')
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users")
    user_ids = cursor.fetchall()

    for user_id in user_ids:
        bot.send_message(user_id[0], message.text)

    bot.reply_to(message, "Рассылка завершена!")

    conn.close()


#################################################################################################################################
#  Очистка бд                                                                                                                   #
#  Так как рейтинг лист выводит всех пользователей из таблицы юзерс, будет не очень если там будет куча учеников из разных групп#
#################################################################################################################################
@bot.message_handler(func=lambda message: message.text == '☠️ Очистка БД')
def handle_clean(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAIw1mVvnA_YvcCURR31sVtPkI-ASdOJAAJbAgACVp29CgAB3yMzQxabnjME')
        bot.reply_to(message, f"🚫 Похоже, у тебя нет доступа в рыбный отдел!")
    else:
        conn = sqlite3.connect('BotDatabase.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users")
        conn.commit()

        bot.reply_to(message, "База данных была очищена, пользователю нужно снова ввести /start чтобы бот внес его в бд.")

        conn.close()


################
#  Команда /all#
################
@bot.message_handler(commands=['all'])
def handle_all(message):
    chat_id = message.chat.id

    conn = sqlite3.connect('BotDatabase.db')
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users")
    usernames = cursor.fetchall()

    marked_message = "Отмечены:\n"
    for username in usernames:
        if username[0] is not None:
            marked_message += f"@{username[0]}\n"

    bot.reply_to(message, marked_message)

    conn.close()

@bot.message_handler(func=lambda message: message.text == '🗑 Выборочная очистка БД')
def handle_cleanv(message):
    chat_id = message.chat.id

    conn = sqlite3.connect('BotDatabase.db')
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT group_name FROM users")
    groups = cursor.fetchall()

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for group in groups:
        keyboard.add(types.KeyboardButton(group[0]))

    bot.send_message(chat_id, "Выберите группу для удаления:", reply_markup=keyboard)

    bot.register_next_step_handler(message, lambda message: delete_users(message, groups))

def delete_users(message, groups):
    chat_id = message.chat.id
    group_to_delete = message.text

    if (group_to_delete,) in groups:
        conn = sqlite3.connect('BotDatabase.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE group_name=?", (group_to_delete,))
        conn.commit()
        conn.close()
        bot.send_message(chat_id, f"✅ Пользователи из группы {group_to_delete} были удалены")
    else:
        bot.send_message(chat_id, "❌ Этой группы не существует или она уже удалена")


#####################
#  Старт работы бота#
#####################
def main():
    print('Бот нячал работу!!')
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(1)

if __name__ == "__main__":
    main()