from config import token
import telebot
from telebot import types
from functions import *

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def Start(message):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    sing_in_button = types.KeyboardButton(text='регистрация')
    markup.add(sing_in_button)

    bot.send_message(chat_id=message.chat.id, text='привет, это бот молодёжных служений в городе Липецке', reply_markup=markup)
    bot.register_next_step_handler(message, Firs_keyboard_check, message)

bot.polling()