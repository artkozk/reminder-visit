import telebot
from telebot import types
import sqlite3
import schedule
import time
from threading import Thread
import datetime
from config import token, admin_id


Bible = {
    '1': 'Бытие глава 1, от Матфея глава 1',
    '2': 'Бытие глава 3, от Матфея глава 3',
    '3': 'Бытие глава 4, от Матфея глава 4',
    '4': 'Бытие глава 5, от Матфея глава 5',
    '5': 'Бытие глава 6, от Матфея глава 6',
    '6': 'Бытие глава 7, от Матфея глава 7',
    '7': 'Бытие глава 8, от Матфея глава 8',
    '8': 'Бытие глава 9, от Матфея глава 9',
    '9': 'Бытие глава 1, от Матфея глава 1',
    '10': 'Бытие глава 2, от Матфея глава 2',
    '11': 'Бытие глава 3, от Матфея глава 3',
    '12': 'Бытие глава 4, от Матфея глава 4',
    '13': 'Бытие глава 5, от Матфея глава 5',
    '14': 'Бытие глава 6, от Матфея глава 6',
    '15': 'Бытие глава 7, от Матфея глава 7',
    '16': 'Бытие глава 8, от Матфея глава 8',
    '17': 'Бытие глава 9, от Матфея глава 9',
    '18': 'Бытие глава 10, от Матфея глава 10',
    '19': 'Бытие глава 11, от Матфея глава 11',
    '20': 'Бытие глава 22, от Матфея глава 12',
    '21': 'Бытие глава 13, от Матфея глава 13',
    '22': 'Бытие глава 14, от Матфея глава 14',
    '23': 'Бытие глава 15, от Матфея глава 15',
    '24': 'Бытие глава 16, от Матфея глава 16',
    '25': 'Бытие глава 17, от Матфея глава 17',
    '26': 'Бытие глава 18, от Матфея глава 18',
    '27': 'Бытие глава 19, от Матфея глава 19',
    '28': 'Бытие глава 20, от Матфея глава 20',
    '29': 'Бытие глава 21, от Матфея глава 21',
    '30': 'Бытие глава 22, от Матфея глава 22',
    '31': 'Бытие глава 23, от Матфея глава 23'
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
                yes_count TEXT DEFAULT '0',
                last_yes_date TEXT DEFAULT ''
            )
        ''')
        conn.commit()

initialize_db()

active_registrations = set()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    if user_id in active_registrations:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text='пожертвовать'), types.KeyboardButton(text='что читать сегодня?'))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM Users WHERE id = ?', (user_id,))
        result = cursor.fetchone()

    if result:
        funk(message)
    else:
        bot.send_message(message.chat.id, 'Привет! Это бот молодёжных служений, для начала пройди регистрацию.')
        active_registrations.add(user_id)
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
        bot.register_next_step_handler(message, confirm_registration, name, second_name, age)
    except ValueError:
        bot.send_message(message.chat.id, 'Пожалуйста, введи числовое значение возраста.')
        bot.register_next_step_handler(message, save_age, name, second_name)

def confirm_registration(message, name, second_name, age):
    if message.text.lower() == 'да':
        user_id = message.chat.id
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if age > 2147483647:
                age = 2147483647
            cursor.execute(
                'INSERT INTO Users (id, name, second_name, age) VALUES (?, ?, ?, ?)',
                (user_id, name, second_name, age)
            )
            conn.commit()
        bot.send_message(message.chat.id, 'Вы зарегистрированы.')
        active_registrations.remove(user_id)
        funk(message)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, воспользуйся кнопками.')
        sing_in(message)

def funk(message):
    user_id = message.chat.id
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM Users WHERE id = ?', (user_id,))
        result = cursor.fetchone()

    if result:
        name = result[0]
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
        bot.send_message(message.chat.id,
                         'Пожертвование можно совершить по этой ссылке: https://www.tinkoff.ru/rm/beshkarev.daniil1/Zv7pR81683\n\nСпасибо за ваше открытое сердце!')
    elif message.text == 'что читать сегодня?':
        read(message.chat.id)
    elif message.text == "Statistik1":
        send_statistics_to_admin(message)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, воспользуйся кнопками.')
    bot.register_next_step_handler(message, funk_check)

def read(user_id):
    day = datetime.datetime.now().strftime("%d").lstrip('0')
    read = Bible.get(day, 'чтение не назначено')
    bot.send_message(chat_id=user_id,
                     text=f'Сегодня к прочтению предлагается: {read}\nНажми на кнопку, как только прочитаешь.')
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='прочитал', callback_data='yes'),
               types.InlineKeyboardButton(text='не буду сегодня читать', callback_data='no'))
    bot.send_message(chat_id=user_id, text='Выберите:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def check_read(call):
    user_id = call.message.chat.id
    today_date = datetime.date.today().isoformat()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT last_yes_date FROM Users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        last_yes_date = result[0] if result else ''

    if call.data == 'yes':
        if last_yes_date == today_date:
            bot.answer_callback_query(call.id, 'Вы уже отметили чтение на сегодня.')
        else:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE Users SET yes_count = yes_count + 1, last_yes_date = ? WHERE id = ?',
                               (today_date, user_id))
                conn.commit()
            bot.answer_callback_query(call.id, 'Продолжай в том же духе!')
        # Optionally edit the message or remove it
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text='Вы прочитали этот отрывок сегодня. Молодец!',
            reply_markup=None
        )
    elif call.data == 'no':
        bot.answer_callback_query(call.id, 'Обязательно прочитай в следующий раз!')
        # Optionally edit the message or remove it
        bot.edit_message_text(
            chat_id=user_id,
            message_id=call.message.message_id,
            text='Вы выбрали не читать сегодня. Попробуйте в следующий раз.',
            reply_markup=None
        )


def send_statistics_to_admin(message):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, second_name, yes_count FROM Users')
        stats = cursor.fetchall()

    stats_message = 'Статистика пользователей:\n'
    if stats:
        for name, second_name, yes_count in stats:
            stats_message += f'{name} {second_name}: {yes_count} раз прочитал(а) Библию.\n'
    else:
        stats_message = 'Нет данных для отображения.'

    bot.send_message(admin_id, stats_message)

def job():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Job running at {now}")

schedule.every().day.at("09:00").do(job)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_thread = Thread(target=run_schedule)
    schedule_thread.start()
    bot.polling(none_stop=True)
