from config import token
import telebot
from telebot import types

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def Start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    sing_in_button = types.KeyboardButton(text='регистрация')
    markup.add(sing_in_button)

    bot.send_message(chat_id=message.chat.id, text='привет, это бот молодёжных служений в городе Липецке', reply_markup=markup)
    bot.register_next_step_handler(message, Firs_keyboard_check, message)
def Firs_keyboard_check(message):
    if message.text == 'регистрация':
        bot.send_mesasge(message.chat_id, text='Напишите ваше имя')
    else:
        bot.send_message(message.chat_id, text='')
bot.polling()