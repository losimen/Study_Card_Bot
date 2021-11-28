import telebot
import config
import uuid
import copy
from db import BotDB
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
questions = {}
sessions = {}


def bot_send_questions(user_id, competitor_id):
    question = questions[user_id][0]

    bot.send_message(user_id, "<b>Your questions left: </b>\n" + print_questions(questions[user_id]) +
                     f"<b>Opponent questions left: {len(questions[competitor_id])}</b>", parse_mode='html')
    bot.send_message(user_id, "<b>Wait for opponent answer!\n</b>You asked question: " + question, parse_mode='html')

    sent = bot.send_message(competitor_id, "<b>‼️Your turn, answer the question:</b> " + question, parse_mode='html')
    return sent


def print_questions(arr):
    string = ""
    i = 1
    for q in arr:
        string += f"{i}." + q + "\n"
        i += 1
    return string


def get_competitor_id(user_id, session_id):
    temp_session = copy.deepcopy(sessions)
    temp_session[session_id].remove(user_id)

    return temp_session[session_id][0]


def check_answer(message, session_id):
    user_id = get_competitor_id(message.chat.id, session_id)

    keyboard = types.InlineKeyboardMarkup(row_width=1)

    button1 = types.InlineKeyboardButton("✅True", callback_data='answer_true')
    button2 = types.InlineKeyboardButton("❌False", callback_data='answer_false')

    keyboard.add(button1, button2)

    bot.send_message(user_id, "<b>Opponent answer: <i>" + message.text + "</i></b>", reply_markup=keyboard, parse_mode='html')


def ask_question(user_id, session_id, prev_stat):
    competitor_id = get_competitor_id(user_id, session_id)

    if prev_stat:
        bot.send_message(user_id, "<b>✅You was right✅</b>", parse_mode='html')
        questions[competitor_id].pop(0)

        if len(questions[competitor_id]) == 0:
            dat = BotDB('StudyCardGameDatabase.db')

            bot.send_message(user_id, f"<b>You won🥳</b>\n<b>Total score:{5}<\b>",
                             parse_mode='html')
            dat.update_score(user_id, 5)

            bot.send_message(competitor_id, f"<b>You won🥳</b>\n<b>Total score:{5 - len(questions[user_id])}<\b>",
                             parse_mode='html')
            dat.update_score(competitor_id, 5 - len(questions[user_id]))
            return
    else:
        bot.send_message(user_id, "<b>❌You failed this question❌</b>", parse_mode='html')

    sent = bot_send_questions(user_id, competitor_id)
    bot.register_next_step_handler(sent, check_answer, session_id)


def start_game(user_id, session_id):
    competitor_id = get_competitor_id(user_id, session_id)

    if len(questions[user_id]) == len(questions[competitor_id]):
        sent = bot_send_questions(user_id, competitor_id)
        bot.register_next_step_handler(sent, check_answer, session_id)


def ask_id(message):
    session_id = message.text
    if session_id not in sessions.keys():
        bot.send_message(message.chat.id, "Error😔.There isn't such a session",
                         parse_mode='html')
        join_game(message)
        return

    creator_id = sessions[session_id][0]

    bot.send_message(creator_id, "User has joined")

    questions[message.chat.id] = []
    sessions[session_id].append(message.chat.id)
    set_cards(message.chat.id, session_id)
    set_cards(creator_id, session_id)


def join_game(message):
    sent = bot.send_message(message.chat.id, "<b>Good👍, enter code of your session:</b>", parse_mode='html')
    bot.register_next_step_handler(sent, ask_id)


def create_game(message):
    bot.send_message(message.chat.id, "<b>Well,👀 creating session...</b>", parse_mode='html')
    # creating session
    session_id = uuid.uuid4().hex[:5]
    sessions[session_id] = [message.chat.id]

    questions[message.chat.id] = []

    bot.send_message(message.chat.id,
                     f"Your session code: <b> {session_id} </b> \nTo continue, you need to send this code to a friend\nThen the game will start",
                     parse_mode='html')


def save_cards(message, session_id):
    question_id = len(questions[message.chat.id])
    questions[message.chat.id].append(message.text)

    if question_id >= 4:
        bot.send_message(message.chat.id, ",".join(questions[message.chat.id]))
        start_game(message.chat.id, session_id)
        return

    sent = bot.send_message(message.chat.id, f"Enter {question_id + 2} question: ")
    bot.register_next_step_handler(sent, save_cards, session_id)


def set_cards(user_id, session_id):
    bot.send_message(user_id, "In order to continue you need to enter 5 questions for the opponent")
    sent = bot.send_message(user_id, "Enter 1 question: ")
    bot.register_next_step_handler(sent, save_cards, session_id)


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     'Hello, {0.first_name}!\nI am - <b>{1.first_name}</b> bot, which...'.format(message.from_user,
                                                                                                 bot.get_me()),
                     parse_mode='html')
    main_menu(message)


@bot.message_handler(commands=['main_menu'])
def main_menu(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)

    button1 = types.KeyboardButton("Start game")
    button2 = types.KeyboardButton("Top players🏆")
    button3 = types.KeyboardButton("Help🆘")

    keyboard.add(button1, button2, button3)

    bot.send_message(message.chat.id, "Main menu\nChoose, what to do next", reply_markup=keyboard,
                     parse_mode='html')


@bot.message_handler(content_types=['text'])
def any_text(message):
    if message.chat.type == "private":
        if message.text == "Start game":
            keyboard = types.InlineKeyboardMarkup(row_width=1)

            button1 = types.InlineKeyboardButton("Create session", callback_data='create_game')
            button2 = types.InlineKeyboardButton("Join to the session", callback_data='join_game')

            keyboard.add(button1, button2)

            bot.send_message(message.chat.id, "Choose, what to do next", reply_markup=keyboard)
        elif message.text == "Top players🏆":
            db = BotDB('StudyCardGameDatabase.db')
            score = db.score_results()

            bot.send_message(message.chat.id,
                             f"\tTop 5 players:\n"+
                             f"#1 🥇{score[0][0]}: {score[0][1]}\n" +
                             f"#2 🥈{score[1][0]}:  {score[1][1]}\n" +
                             f"#3 🥉{score[2][0]}:  {score[2][1]}\n" +
                             f"#4 {score[3][0]}:  {score[3][1]}\n" +
                             f"#5 {score[4][0]}:  {score[4][1]}\n"
                             f"<b>Your total score: </b>")

        elif message.text == "Help🆘":
            bot.send_message(message.chat.id, "Creator: @lamens")
        else:
            bot.send_message(message.chat.id, "Error😔\nI don't know what to do😓")
            main_menu(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'create_game':
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="Choose, what to do next",
                                      reply_markup=None)

                create_game(call.message)

            elif call.data == 'join_game':
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="Choose, what to do next",
                                      reply_markup=None)

                join_game(call.message)

            elif call.data == 'answer_true':
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="<b><i>" + call.message.text + "</i></b>",
                                      reply_markup=None,
                                      parse_mode='html')
                competitor_id = get_competitor_id(call.message.chat.id, list(sessions.keys())[0])
                ask_question(competitor_id, list(sessions.keys())[0], True)

            elif call.data == 'answer_false':
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="<b><i>" + call.message.text + "</i></b>",
                                      reply_markup=None,
                                      parse_mode='html')
                competitor_id = get_competitor_id(call.message.chat.id, list(sessions.keys())[0])
                ask_question(competitor_id, list(sessions.keys())[0], False)

    except Exception as wht:
        print(repr(wht))


bot.polling(none_stop=True)
