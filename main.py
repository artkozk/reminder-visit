import telebot
from telebot import types
import sqlite3
import schedule
import time
from threading import Thread
import datetime
from config import token, admin_id

Bible = {
    '1': 'лука 1', '2': 'лука 1', '3': 'лука 1', '4': 'лука 1', '5': 'лука 1',
    '6': 'лука 1', '7': 'лука 1', '8': 'лука 1', '9': 'лука 1', '10': 'лука 1',
    '11': 'лука 1', '12': 'лука 1', '14': 'лука 1', '15': 'лука 1', '16': 'лука 1',
    '17': 'лука 1', '18': 'лука 1', '19': 'лука 1', '20': 'лука 12', '21': 'лука 1',
    '22': 'лука 1', '23': 'лука 1', '24': 'лука 1', '25': 'лука 1', '26': 'лука 1',
    '27': 'лука 1', '28': 'лука 1', '29': 'лука 1', '30': 'лука 1', '31': 'лука 1'
}

bot = telebot.TeleBot(token)

def initialize_db():
    conn = sqlite3.connect("bible_bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            second_name TEXT,
            yes_count INTEGER DEFAULT 0,
            last_yes_date TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()

initialize_db()

@bot.message_handler(commands=['start'])
def Start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text='пожертвовать'), types.KeyboardButton(text='что читать сегодня?'))
    user_id = message.chat.id

    conn = sqlite3.connect("bible_bot.db")
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM Users WHERE id = ?', (user_id,))
    result = cursor.fetchone()

    if result:
        conn.close()
        Funk(message)
    else:
        conn.close()
        bot.send_message(message.chat.id, 'Привет! Это бот молодёжных служений, для начала пройди регистрацию.')
        Sing_in(message)

def Sing_in(message):
    bot.send_message(message.chat.id, 'Введи своё имя:')
    bot.register_next_step_handler(message, Save_name)

def Save_name(message):
    name = message.text
    bot.send_message(message.chat.id, 'Введи свою фамилию:')
    bot.register_next_step_handler(message, Save_second_name, name)

def Save_second_name(message, name):
    second_name = message.text
    bot.send_message(message.chat.id, 'Введи свой возраст:')
    bot.register_next_step_handler(message, Save_age, name, second_name)

def Save_age(message, name, second_name):
    try:
        age = int(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(text='да'), types.KeyboardButton(text='нет'))
        bot.send_message(
            message.chat.id,
            f'Имя: {name}\nФамилия: {second_name}\nВозраст: {age}\nВсе верно?',
            reply_markup=markup
        )
        bot.register_next_step_handler(message, Ask_true, name, second_name, age)
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введи числовое значение возраста.')
        bot.register_next_step_handler(message, Save_age, name, second_name)

def Ask_true(message, name, second_name, age):
    if message.text.lower() == 'да':
        user_id = message.chat.id
        conn = sqlite3.connect("bible_bot.db")
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Users (id, name, second_name, age) VALUES (?, ?, ?, ?)',
            (user_id, name, second_name, age)
        )
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, 'Вы зарегистрированы.')
        Funk(message)
    elif message.text.lower() == 'нет':
        Sing_in(message)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, воспользуйся кнопками.')
        bot.register_next_step_handler(message, Ask_true, name, second_name, age)

def Funk(message):
    user_id = message.chat.id
    conn = sqlite3.connect("bible_bot.db")
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM Users WHERE id = ?', (user_id,))
    name = cursor.fetchone()

    if name:
        name = name[0]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(text='пожертвовать'), types.KeyboardButton(text='что читать сегодня?'))
        bot.send_message(
            message.chat.id,
            f'{name}, ты можешь воспользоваться кнопками:',
            reply_markup=markup
        )
        bot.register_next_step_handler(message, Funk_check)
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка. Попробуйте снова.')
    conn.close()

def Funk_check(message):
    if message.text == 'пожертвовать':
        bot.send_message(message.chat.id, 'Функция "пожертвовать" в разработке.')
    elif message.text == 'что читать сегодня?':
        Read(message.chat.id)
    elif message.text == "Statistik1":
        Send_statistics_to_admin()
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, воспользуйся кнопками.')
        bot.register_next_step_handler(message, Funk_check)

def Read(user_id):
    day = datetime.datetime.now().strftime("%d").lstrip('0')
    read = Bible.get(day, 'чтение не назначено')
    bot.send_message(chat_id=user_id, text=f'Сегодня к прочтению предлагается: {read}\nНажми на кнопку, как только прочитаешь.')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='прочитал', callback_data='yes'), types.InlineKeyboardButton(text='не буду сегодня читать', callback_data='no'))
    bot.send_message(chat_id=user_id, text='Выберите:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def Check_read(call):
    user_id = call.message.chat.id
    today_date = datetime.date.today().isoformat()

    conn = sqlite3.connect("bible_bot.db")
    cursor = conn.cursor()
    cursor.execute('SELECT last_yes_date FROM Users WHERE id = ?', (user_id,))
    last_yes_date = cursor.fetchone()[0]

    if call.data == 'yes':
        if last_yes_date == today_date:
            bot.send_message(call.message.chat.id, 'Вы уже отметили чтение на сегодня.')
        else:
            cursor.execute('UPDATE Users SET yes_count = yes_count + 1, last_yes_date = ? WHERE id = ?', (today_date, user_id))
            conn.commit()
            bot.send_message(call.message.chat.id, 'Продолжай в том же духе!')
    elif call.data == 'no':
        bot.send_message(call.message.chat.id, 'Обязательно прочитай в следующий раз!')

    conn.close()
    Funk(call.message)

def Send_statistics_to_admin():
    conn = sqlite3.connect("bible_bot.db")
    cursor = conn.cursor()
    cursor.execute('SELECT name, second_name, yes_count FROM Users')
    stats = cursor.fetchall()
    conn.close()

    if stats:
        stats_message = "Статистика чтения:\n\n"
        for name, second_name, yes_count in stats:
            stats_message += f'{name} {second_name}: прочитал {yes_count} раз(а)\n'
        bot.send_message(admin_id, stats_message)
    else:
        bot.send_message(admin_id, "Нет данных для статистики.")

@bot.message_handler(commands=['stats'])
def Stats(message):
    if message.chat.id == admin_id:
        Send_statistics_to_admin()
    else:
        bot.send_message(message.chat.id, 'У вас нет прав для получения статистики.')

def send_thursday_reminder():
    conn = sqlite3.connect("bible_bot.db")
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM Users')
    users = cursor.fetchall()
    for user in users:
        user_id = user[0]
        cursor.execute('SELECT name FROM Users WHERE id = ?', (user_id,))
        name = cursor.fetchone()
        bot.send_message(chat_id=user_id, text=f'Привет, {name[0]}\nприходи сегодня в 19:00 на молодёжное служение. Буду рад видеть тебя в нашей дружной компании 😁')
    conn.close()

def send_daily_reminder():
    conn = sqlite3.connect("bible_bot.db")
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM Users')
    users = cursor.fetchall()
    for user in users:
        user_id = user[0]
        Read(user_id)
    conn.close()

schedule.every().thursday.at("10:00").do(send_thursday_reminder)
schedule.every().day.at("14:00").do(send_daily_reminder)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

Thread(target=run_schedule).start()

bot.polling(none_stop=True)
