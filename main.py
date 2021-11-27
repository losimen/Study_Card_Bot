import telebot
import config
import time
from telebot import types

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     'Привіт, {0.first_name}!\nЯ - <b>{1.first_name}</b> бот, який...'.format(message.from_user,
                                                                                              bot.get_me()),
                     parse_mode='html')
    main_menu(message)


@bot.message_handler(commands=['main_menu'])
def main_menu(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    button1 = types.KeyboardButton("Почати гру")
    button2 = types.KeyboardButton("Таблиця гравців")
    button3 = types.KeyboardButton("Допомога")

    keyboard.add(button1, button2, button3)

    bot.send_message(message.chat.id, "Головне меню\nОбери, що будемо робити далі", reply_markup=keyboard,
                     parse_mode='html')


@bot.message_handler(commands=['set_cards'])
def set_cards(message):
    user_stat = True
    # check if user is at the game
    if user_stat:
        questions = [None] * 5
        bot.send_message(message.chat.id, "Для того, щоб продовжити тобі потрібно ввести 5 питань для опонента:")

    else:
        bot.send_message(message.chat.id, "Помилка😔\nТобі спершу потрібно увійти або створити сесію",
                         parse_mode='html')

    main_menu(message)


@bot.message_handler(commands=['do_turn'])
def do_turn(message):
    user_stat = False
    # check if user is at the game
    if user_stat:
        # print user data
        pass
        # do turn
    else:
        bot.send_message(message.chat.id, "Помилка😔\nТобі спершу потрібно увійти або створити сесію",
                         parse_mode='html')


@bot.message_handler(content_types=['text'])
def any_text(message):
    if message.chat.type == "private":
        # check if user is at the game
        if False:
            bot.send_message(message.chat.id, "Помилка😔\nСпершу потрібно завершити теперішню сесію",
                             parse_mode='html')

        if message.text == "Почати гру":
            keyboard = types.InlineKeyboardMarkup(row_width=1)

            button1 = types.InlineKeyboardButton("Створити сесію", callback_data='create_game')
            button2 = types.InlineKeyboardButton("Увійти до сесії", callback_data='join_game')

            keyboard.add(button1, button2)

            bot.send_message(message.chat.id, "Обери, що тобі підходить", reply_markup=keyboard)
        elif message.text == "Таблиця гравців":
            bot.send_message(message.chat.id, "Скоро...")
        elif message.text == "Допомога":
            bot.send_message(message.chat.id, "Звернись до: @lamens")
        else:
            bot.send_message(message.chat.id, "Я не знаю такої дії  😓")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline_room(call):
    try:
        if call.message:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Обери, що тобі підходить",
                                  reply_markup=None)

            if call.data == 'create_game':
                bot.send_message(call.message.chat.id, "<b>Добре,👀 створюємо cесію...</b>", parse_mode='html')
                # creating session
                session_id = 0

                bot.send_message(call.message.chat.id,
                                 "Код твоєї сесії: {0}\nЩоби продовжити, тобі потрібно надіслати цей код другу\nТоді гра розпочнеться".format(session_id),
                                 parse_mode='html')
                # wait until another user join session

                wait_counter = 10
                while False:
                    # check if another user joined
                    if True:
                        break

                    time.sleep(5)
                    wait_counter += 1
                # check if another user joined
                if True:
                    set_cards(call.message)
                else:
                    bot.send_message(call.message.chat.id,
                                     "Час очікування, вийшов. Видаляю сесію".format(
                                         session_id),
                                     parse_mode='html')

            elif call.data == 'join_game':
                bot.send_message(call.message.chat.id, "<b>Чудово👍, введи номер сесії:</b>", parse_mode='html')

    except Exception as wht:
        print(repr(wht))


bot.polling(none_stop=True)
