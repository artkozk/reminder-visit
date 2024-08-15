from main import *
def Firs_keyboard_check(message):
    if message.text == 'регистрация':
        bot.register_next_step_handler(message, Sing_in)
    else:
        bot.send_message(message.chat_id, text='Пожалуйста зарегистрируйтесь')
        bot.register_next_step_handler(message, Firs_keyboard_check)
def Sing_in(message):
    bot.send_message(message.chat_id, text='Напишите ваше имя')