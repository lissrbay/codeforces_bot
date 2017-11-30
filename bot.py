# -*- coding: utf-8 -*-
#CFTrainingBot
import config
import telebot
import createuserbase
import problem
import sqlite3
import update

login_input = 0
task = 0
theory_adding = 0
getting_theory = 0
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands = ['help'])
def show_help(message):
    s = ''
    s += "/login - to authorization\n"
    s += "/task - to get random unsolved task\n"
    s += "/theory - to get theory for chosen tag\n"
    s += "/update - to update your submittions\n"
    s += "/stats - to see your statistic"
    bot.send_message(message.chat.id, "Type:\n" + s)


@bot.message_handler(commands=['start'])
def sayhellotoeveryone(message):
    bot.send_message(message.chat.id, "Hello!")
    bot.send_message(message.chat.id, "Type /help to see list of commands.")


#Not availible for users
#@bot.message_handler(commands=['add'])
#def add_theory(message):
#    global theory_adding
#    bot.send_message(message.chat.id, "Gimme tag and link")
#   theory_adding = 1

#@bot.message_handler(func = lambda message: theory_adding == 1)
#def add_theory2(message):
#    s = message.text.split()
#    update.update_theory_base(s[0], s[1])
#    global theory_adding
#    theory_adding = 0


@bot.message_handler(commands=['theory'])
def get_theory(message):
    global getting_theory
    bot.send_message(message.chat.id, "Print tag for theory.\nList of tags:\n - math \n - dp \n - greedy \n - strings \n - trees \n - graphs \n - geometry \n - combinatorics")
    getting_theory = 1


@bot.message_handler(func = lambda message: getting_theory == 1)
def get_theory2(message):
    global getting_theory
    getting_theory = 0

    bot.send_message(message.chat.id, str(problem.get_theory_from_tag(message.text)))


@bot.message_handler(commands =['login'])
def get_login(message):
    global name
    settings = sqlite3.connect("settings.db")
    conn = settings.cursor()
    conn.execute("select * from users where chat_id = '" + str(message.chat.id) + "'")
    name = conn.fetchone()
    settings.close()
    if name != None:
        bot.send_message(message.chat.id, "Previous handle: " + str(name[1]))
    else:
        bot.send_message(message.chat.id, "Previous handle: None")

    bot.send_message(message.chat.id, "Type new handle: ")
    global login_input
    login_input = 1


@bot.message_handler(func = lambda message: login_input == 1)
def get_login2(message):
    if createuserbase.check_username(message.text):
        bot.send_message(message.chat.id, "Invalid handle.")
        return 0
    settings = sqlite3.connect("settings.db")
    conn = settings.cursor()
    conn.execute("select * from users where chat_id = '" + str(message.chat.id) + "'")
    name = conn.fetchone()
    settings.close()
    if name == None:
        bot.send_message(message.chat.id, "Creating base...")
        createuserbase.init_user(message.text, message.chat.id)
        bot.send_message(message.chat.id, "Done!")
    else:
        createuserbase.clean_base(name[1])
        createuserbase.clean_base(message.text)
        bot.send_message(message.chat.id, "Creating base...")
        createuserbase.init_user(message.text, message.chat.id)
        bot.send_message(message.chat.id, "Done!")
    global login_input
    login_input = 0


@bot.message_handler(commands=['task'])
def task(message):
    global task
    bot.send_message(message.chat.id, "Which kind of task you need?\nList of tags:\n - math \n - dp \n - greedy \n - strings \n - trees \n - graphs \n - geometry \n - combinatorics")
    task = 1

@bot.message_handler(commands=['stats'])
def stats(message):
    settings = sqlite3.connect("settings.db")
    conn = settings.cursor()
    conn.execute("select * from users where chat_id = '" + str(message.chat.id) + "'")
    name = conn.fetchone()
    settings.close()
    problem.create_text_stats(name[1])
    img = open(name[1] + ".png", "rb")
    bot.send_photo(message.chat.id, img)
    img.close()
    if problem.create_stats_picture(name[1]):
        bot.send_message(message.chat.id, "Sorry, you haven't solved tasks.")
        return 0
    img = open(name[1] + ".png", "rb")
    bot.send_photo(message.chat.id, img)
    img.close()


@bot.message_handler(commands=['update'])
def up_to_date(message):
    bot.send_message(message.chat.id, "Updating base...")
    update.cf_update()
    settings = sqlite3.connect("settings.db")
    conn = settings.cursor()
    conn.execute("select * from users where chat_id = '" + str(message.chat.id) + "'")
    name = conn.fetchone()
    settings.close()
    if name == None:
        bot.send_message(message.chat.id, "You should login before update your submittions.")
    else:
        update.update_user(name[1], name[0], name[2])
    bot.send_message(message.chat.id, "Done!")


@bot.message_handler(func = lambda message: task == 1)
def get_task(message):
    global task
    settings = sqlite3.connect("settings.db")
    conn = settings.cursor()
    conn.execute("select * from users where chat_id = '" + str(message.chat.id) + "'")
    name = conn.fetchone()
    settings.close()
    if name == None:
        bot.send_message(message.chat.id, "You should login before get tasks.")
    else:
        bot.send_message(message.chat.id, problem.get_unsolved_problem(message.text, name[1]))
    task = 0


@bot.message_handler(commands = ['bite'])
def bite(message):
    bot.send_message(message.chat.id, "Кусь тебя за ушко, мурмурмур!:3")


@bot.message_handler(content_types=['text'])
def reply(message):
    bot.send_message(message.chat.id, "Hmm...")


if __name__ == '__main__':
     bot.polling(none_stop = True)