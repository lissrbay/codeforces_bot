#Ребята, не стоит вскрывать этот код.
#Вы молодые, хакеры, вам все легко. Это не то.
#Это не Stuxnet и даже не шпионские программы ЦРУ. Сюда лучше не лезть.
#Серьезно, любой из вас будет жалеть. Лучше закройте компилятор и забудьте что там писалось.
#Я вполне понимаю что данным сообщением вызову дополнительный интерес, но хочу сразу предостеречь пытливых - стоп.
#Остальные просто не найдут.

import sqlite3
import os
import random
import matplotlib.pyplot as plt

state = {'math', "strings", "trees", "graphs", "dp", "greedy", "geometry", "combinatorics"}
def get_unsolved_problem(tag, username):
    if not tag in state:
        return "Incorrect tag."
    random.seed()
    conn = sqlite3.connect(username + '.db')
    conn2 = sqlite3.connect('cf.db')
    cursor = conn.cursor()
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT * FROM " + tag)
    a = list()
    x = cursor2.fetchone()
    while x != None:
        cursor.execute("SELECT * FROM result WHERE problem = '" + str(x[0]) + "' AND diff = '" + str(x[1]) + "' AND NOT verdict = 'OK'")
        y = cursor.fetchone()
        if y != None:
            a.append(y)
        x = cursor2.fetchone()

    conn.close()
    conn2.close()

    if len(a) > 0:
        ind1 = random.randint(0, len(a) - 1)
        s1 = str(a[ind1][0]) + '/' + a[ind1][1]
        a.pop(ind1)
        return 'http://codeforces.com/problemset/problem/' + s1
    else:
        return "You have solved all tasks with this tag, nice!"

def get_theory_from_tag(tag):
    if not tag in state:
        return "Incorrect tag."
    base = sqlite3.connect("theory.db")
    conn = base.cursor()
    conn.execute("select * from " + tag)
    x = conn.fetchone()
    s = ""
    while x != None:
        s += str(x[0]) + '\n'
        x = conn.fetchone()
    base.close()
    return s

class Pair():
    def __init__(self, first, second):
        self.first = first
        self.second = second

def create_stats_picture(username):
    conn = sqlite3.connect(username + '.db')
    conn2 = sqlite3.connect('cf.db')
    cursor = conn.cursor()
    cursor2 = conn2.cursor()
    a = list()
    b = list()
    leg = list()
    sum = 0
    for i in state:
        cursor2.execute("SELECT * FROM " + str(i))
        x = cursor2.fetchone()
        count = 0
        while x != None:
            cursor.execute("SELECT * FROM result WHERE problem = '" + str(x[0]) + "' AND diff = '" + str(
                x[1]) + "' AND verdict = 'OK'")
            y = cursor.fetchone()
            if y != None:
                count += 1
            x = cursor2.fetchone()
        a.append(Pair(count, i))
        sum += count

    conn.close()
    conn2.close()
    if sum == 0:
        return True
    for i in range(len(a)):
        if a[i].first / sum != 0:
            b.append(a[i].first / sum)
            leg.append(a[i].second)

    fig1, ax1 = plt.subplots()
    ax1.pie(b,  autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    ax1.legend(leg)
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), username + '.png')
    if os.path.exists(path):
        os.remove(path)
    plt.savefig(username + ".png")
    plt.close()
    return False

def create_text_stats(username):
    verdict = {"COMPILATION_ERROR" : 0, "OK" : 0, "TIME_LIMIT_EXCEEDED" : 0, "WRONG_ANSWER" : 0, "RUNTIME_ERROR" : 0, "MEMORY_LIMIT_EXCEEDED" : 0}
    colors = ['red', 'green', 'tan', 'blue', 'purple', 'orange']
    conn = sqlite3.connect(username + '.db')
    conn2 = sqlite3.connect('cf.db')
    cursor = conn.cursor()
    cursor2 = conn2.cursor()
    count = 0
    a = list()
    b = list()
    for i in state:
        cursor2.execute("SELECT * FROM " + str(i))
        x = cursor2.fetchone()
        while x != None:
            cursor.execute("SELECT * FROM result WHERE problem = '" + str(x[0]) + "' AND diff = '" + str(x[1]) + "'")
            y = cursor.fetchone()
            if y != None:
                for j in verdict.keys():
                    if y[2] == j:
                        verdict[j] += 1
                        count += 1

            x = cursor2.fetchone()

    for i in verdict.keys():
        a.append(i)
        b.append(verdict[i])
    fig1, ax1 = plt.subplots()
    ax1.pie(b, labels = b, colors = colors,
            shadow=True, startangle=90)
    ax1.axis('equal')
    ax1.legend(a)
    ax1.set_title('How many different verdict in last status of problem you have: ')
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), username + '.png')
    if os.path.exists(path):
        os.remove(path)
    plt.savefig(username + ".png")
    conn.close()
    conn2.close()
    plt.close()
    s = username + " has at least one submittions in " + str(count) + " problems"
    return s




