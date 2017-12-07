# -*- coding: utf-8 -*-
#CFTrainingBot
import config
import telebot
import bases.createuserbase
import bases.createcfbase
import bases.problem
import sqlite3
import os
import bases.update

bot = telebot.TeleBot(config.token)


def get_current_state(chat_id):
    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__))+"\\bases\\settings.db")
    conn = settings.cursor()
    conn.execute("select * from users where chat_id = '" + str(chat_id) + "'")
    name = conn.fetchone()
    if name != None:
        return name[4]
    else:
        return False
    settings.close()

def set_state(chat_id, value):
    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\bases\\settings.db")
    conn = settings.cursor()
    conn.execute("update users set state ='" + str(value) + "' where chat_id = '" + str(chat_id) + "'")
    settings.commit()
    settings.close()

@bot.message_handler(commands = ['help'])
def show_help(message):
    s = ''
    s += "/login - to authorization.\n"
    s += "/task - to get random unsolved task.\n"
    s += "/theory - to get theory for chosen tag.\n"
    s += "/stats - to see your statistic."
    bot.send_message(message.chat.id, "Type:\n" + s)


@bot.message_handler(commands=['start'])
def sayhellotoeveryone(message):
    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\bases\\settings.db")
    conn = settings.cursor()
    bot.send_message(message.chat.id, "Hello!")
    bot.send_message(message.chat.id, "Type /help to see list of commands.")
    conn.execute("insert into users values (?, ?, ?, ?, ?)", (str(message.chat.id), "None", "NULL", "0", config.States.S_START.value))
    settings.commit()
    settings.close()


#Not available for users
@bot.message_handler(commands=['add'])
def add_theory(message):
    bot.send_message(message.chat.id, "Gimme tag and link")
    set_state(message.chat.id, config.States.S_THEORY_ADDING.value)


@bot.message_handler(func = lambda message: get_current_state(message.chat.id) == config.States.S_THEORY_ADDING.value)
def add_theory2(message):
    s = message.text.split()
    bases.update.update_theory_base(s[0], s[1])
    set_state(message.chat.id, config.States.S_START.value)


@bot.message_handler(commands=['theory'])
def get_theory(message):
    bot.send_message(message.chat.id, "Print tag for theory.\nList of tags:\n - math \n - dp \n - greedy \n - strings \n - trees \n - graphs \n - geometry \n - combinatorics")
    set_state(message.chat.id, config.States.S_THEORY.value)


@bot.message_handler(func = lambda message: get_current_state(message.chat.id) == config.States.S_THEORY.value)
def get_theory2(message):
    bot.send_message(message.chat.id, str(bases.problem.get_theory_from_tag(message.text)))
    set_state(message.chat.id, config.States.S_START.value)


@bot.message_handler(commands =['login'])
def get_login(message):
    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\bases\\settings.db")
    conn = settings.cursor()
    conn.execute("select * from users where chat_id = '" + str(message.chat.id) + "'")
    name = conn.fetchone()
    if name != None:
        bot.send_message(message.chat.id, "Previous handle: " + str(name[1]))
    else:
        bot.send_message(message.chat.id, "Previous handle: None")
    settings.close()
    bot.send_message(message.chat.id, "Type new handle: ")
    set_state(message.chat.id, config.States.S_LOGIN.value)


@bot.message_handler(func = lambda message: get_current_state(message.chat.id) == config.States.S_LOGIN.value)
def get_login2(message):
    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\bases\\settings.db")
    conn = settings.cursor()
    if bases.createuserbase.check_username(message.text):
        bot.send_message(message.chat.id, "Invalid handle.")
        set_state(message.chat.id, config.States.S_START.value)
        return 0

    conn.execute("select * from users where chat_id = '" + str(message.chat.id) + "'")
    name = conn.fetchone()
    settings.close()
    bases.update.cf_update()
    bases.createuserbase.clean_base(name[1])
    bases.createuserbase.clean_base(message.text)
    bot.send_message(message.chat.id, "Creating base...")
    bases.createuserbase.init_user(message.text, message.chat.id)
    bot.send_message(message.chat.id, "Done!")
    set_state(message.chat.id, config.States.S_START.value)


@bot.message_handler(commands=['task'])
def task(message):
    s = "Which kind of task you need?\n"
    s += "List of tags:\n - math \n - dp \n - greedy \n - strings"
    s += "\n - trees \n - graphs \n - geometry \n - combinatorics"
    s += "\nYou may combine tags and difficults e.x. write '"'dp math AB'"' to get task with these tags and difficults."
    bot.send_message(message.chat.id, s)
    set_state(message.chat.id, config.States.S_GET_TASK.value)


@bot.message_handler(func = lambda message: get_current_state(message.chat.id) == config.States.S_GET_TASK.value)
def get_task(message):
    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\bases\\settings.db")
    conn = settings.cursor()
    conn.execute("select * from users where chat_id = '" + str(message.chat.id) + "'")
    name = conn.fetchone()
    settings.close()
    if name == None:
        bot.send_message(message.chat.id, "You should login before get tasks.")
    else:
        bases.update.update_user(name[1], name[0], name[2])
        bot.send_message(message.chat.id, bases.problem.get_unsolved_problem(message.text, name[1]))
    set_state(message.chat.id, config.States.S_START.value)


@bot.message_handler(commands=['stats'])
def stats(message):
    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\bases\\settings.db")
    conn = settings.cursor()
    conn.execute("select * from users where chat_id = '" + str(message.chat.id) + "'")
    name = conn.fetchone()
    settings.close()
    if name != None:
        bases.update.update_user(name[1], name[0], name[2])
        bases.problem.create_text_stats(name[1])
        img = open(os.path.abspath(os.path.dirname(__file__)) + "\\bases\\users\\" + name[1] + ".png", "rb")
        bot.send_photo(message.chat.id, img)
        img.close()
        if bases.problem.create_stats_picture(name[1]):
            bot.send_message(message.chat.id, "Sorry, you haven't solved tasks.")
            return 0
        img = open(os.path.abspath(os.path.dirname(__file__)) + "\\bases\\users\\" + name[1] + ".png", "rb")
        bot.send_photo(message.chat.id, img)
        img.close()
    else:
        bot.send_message(message.chat.id, "You should login before getting statistic.")


@bot.message_handler(commands = ['bite'])
def bite(message):
    bot.send_message(message.chat.id, "Кусь тебя за ушко, мурмурмур!:3")


@bot.message_handler(content_types=['text'])
def reply(message):
    bot.send_message(message.chat.id, "Hmm...")


if __name__ == '__main__':
     bot.polling(none_stop = True)