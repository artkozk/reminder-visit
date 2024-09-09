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

def get_db_connection():
    return sqlite3.connect("bible_bot.db")

def initialize_db():
    with get_db_connection() as conn:
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

initialize_db()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text='пожертвовать'), types.KeyboardButton(text='что читать сегодня?'))
    user_id = message.chat.id

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM Users WHERE id = ?', (user_id,))
        result = cursor.fetchone()

    if result:
        funk(message)
    else:
        bot.send_message(message.chat.id, 'Привет! Это бот молодёжных служений, для начала пройди регистрацию.')
        sing_in(message)

def sing_in(message):
    bot.send_message(message.chat.id, 'Введи своё имя:')
    bot.register_next_step_handler(message, save_name)

def save_name(message):
    name = message.text
    bot.send_message(message.chat.id, 'Введи свою фамилию:')
    bot.register_next_step_handler(message, save_second_name, name)

def save_second_name(message, name):
    second_name = message.text
    bot.send_message(message.chat.id, 'Введи свой возраст:')
    bot.register_next_step_handler(message, save_age, name, second_name)

def save_age(message, name, second_name):
    try:
        age = int(message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton(text='да'), types.KeyboardButton(text='нет'))
        bot.send_message(
            message.chat.id,
            f'Имя: {name}\nФамилия: {second_name}\nВозраст: {age}\nВсе верно?',
            reply_markup=markup
        )
        bot.register_next_step_handler(message, ask_true, name, second_name, age)
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введи числовое значение возраста.')
        bot.register_next_step_handler(message, save_age, name, second_name)

def ask_true(message, name, second_name, age):
    if message.text.lower() == 'да':
        user_id = message.chat.id
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO Users (id, name, second_name, age) VALUES (?, ?, ?, ?)',
                (user_id, name, second_name, age)
            )
            conn.commit()
        bot.send_message(message.chat.id, 'Вы зарегистрированы.')
        funk(message)
    elif message.text.lower() == 'нет':
        sing_in(message)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, воспользуйся кнопками.')
        bot.register_next_step_handler(message, ask_true, name, second_name, age)

def funk(message):
    user_id = message.chat.id
    with get_db_connection() as conn:
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
        bot.register_next_step_handler(message, funk_check)
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка. Попробуйте снова.')

def funk_check(message):
    if message.text == 'пожертвовать':
        bot.send_message(message.chat.id, 'Пожертвование можно совершить по этой ссылке: https://www.tinkoff.ru/rm/beshkarev.daniil1/Zv7pR81683\n\nСпасибо за ваше открытое сердце!')
        bot.register_next_step_handler(message, funk_check)
    elif message.text == 'что читать сегодня?':
        read(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, воспользуйся кнопками.')
        bot.register_next_step_handler(message, funk_check)

def read(user_id):
    day = datetime.datetime.now().strftime("%d").lstrip('0')
    read = Bible.get(day, 'чтение не назначено') 
    bot.send_message(chat_id=user_id, text=f'Сегодня к прочтению предлагается: {read}\nНажми на кнопку, как только прочитаешь.')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='прочитал', callback_data='yes'), types.InlineKeyboardButton(text='не буду сегодня читать', callback_data='no'))
    bot.send_message(chat_id=user_id, text='Выберите:', reply_markup=markup)
@bot.callback_query_handler(func=lambda call: True)
def check_read(call):
    user_id = call.message.chat.id
    today_date = datetime.date.today().isoformat()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT last_yes_date FROM Users WHERE id = ?', (user_id,))
        last_yes_date = cursor.fetchone()[0]

        if call.data == 'yes':
            if last_yes_date == today_date:
                bot.send_message(call.message.chat.id, 'Вы уже отметили чтение на сегодня.')
                funk(call.message)
            else:
                cursor.execute('UPDATE Users SET yes_count = yes_count + 1, last_yes_date = ? WHERE id = ?', (today_date, user_id))
                conn.commit()
                bot.send_message(call.message.chat.id, 'Продолжай в том же духе!')
                funk(call.message)
            
            return
        elif call.data == 'no':
            bot.send_message(call.message.chat.id, 'Обязательно прочитай в следующий раз!')
            funk(call.message)
            return

    


def send_statistics_to_admin():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, second_name, yes_count FROM Users')
        stats = cursor.fetchall()

    if stats:
        stats_message = "Статистика чтения:\n\n"
        for name, second_name, yes_count in stats:
            stats_message += f'{name} {second_name}: прочитал {yes_count} раз(а)\n'
        bot.send_message(admin_id, stats_message)
    else:
        bot.send_message(admin_id, "Нет данных для статистики.")

def send_thursday_reminder():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM Users')
        users = cursor.fetchall()

    for user_id, name in users:
        bot.send_message(chat_id=user_id, text=f'Привет, {name}\nприходи сегодня в 19:00 на молодёжное служение. Буду рад видеть тебя в нашей дружной компании 😁')

def send_daily_reminder():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM Users')
        users = cursor.fetchall()

    for user in users:
        user_id = user[0]
        read(user_id)

schedule.every().thursday.at("10:00").do(send_thursday_reminder)
schedule.every().day.at("14:00").do(send_daily_reminder)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

Thread(target=run_schedule).start()

bot.polling(none_stop=True)
