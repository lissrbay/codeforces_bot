import requests
import sqlite3
import os
from bs4 import BeautifulSoup

def cf_update():
    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\settings.db")
    cursor = settings.cursor()
    cursor.execute("select * from last_update_problemset")
    x = cursor.fetchone()

    last_try = x[0]

    url = 'http://codeforces.com/problemset/'
    r = requests.get(url)
    max_page = 0
    available_tags = {'math', "strings", "trees", "graphs", "dp", "greedy"}
    soup = BeautifulSoup(r.text, "lxml")
    base = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\cf.db")
    conn = base.cursor()

    for link in soup.find_all(attrs={"class" : "page-index"}):
        s = link.find('a')
        s2 = s.get("href").split('/')
        max_page = max(max_page, int(s2[3]))

    a = ''
    b = 0
    f = False
    last_update = last_try
    for i in range(1, max_page + 1):
        r = requests.get('http://codeforces.com/problemset/' + '/page/' + str(i))
        soup = BeautifulSoup(r.text, "lxml")
        old = ''
        v = False
        for link in soup.find_all('a'):
            s = link.get('href')
            if s != None and s.find('/problemset') != -1:
                s = s.split('/')
                if len(s) == 5 and old != s[3] + s[4]:
                    if s[3] + s[4] == last_try:
                        v = True
                        break
                    a = s[3]
                    b = s[4]
                    old = s[3] + s[4]
                    if not f:
                        f = True
                        last_update = old
                    conn.execute("insert into problems values (?, ?)", (a, b))
                if len(s) == 4 and s[3] in available_tags:
                    conn.execute("insert into ? values (?, ?)", (s[3], a, b))

        if v:
            break


    base.commit()
    base.close()
    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\settings.db")
    conn = settings.cursor()
    conn.execute("update last_update_problemset set problem = ? where problem = ?", (str(last_update), str(last_try)))
    settings.commit()
    settings.close()

def update_user(username, chat_id, last_update):
    conn = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\users\\" + username + '.db')
    conn2 = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + '\\cf.db')
    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\settings.db")
    cursor = conn.cursor()
    cursor2 = conn2.cursor()
    cursor_settings = settings.cursor()
    cursor_settings.execute("select last_problem from users where chat_id = ?", (str(chat_id), ))
    update_eq = cursor_settings.fetchone()
    cursor_settings.execute("select * from last_update_problemset")
    update_base = cursor_settings.fetchone()
    last_problem = update_base[0]
    if update_eq[0] != update_base[0]:
        cursor2.execute("SELECT * FROM problems")
        x = cursor2.fetchone()
        while x != None:
            cursor.execute("select * from result where problem = ? and diff = ?", (str(x[0]), str(x[1])))
            x2 = cursor.fetchone()
            if x2 == None:
                cursor.execute("insert into result values (?, ?, ? )", (x[0], x[1], "NULL"))
            last_problem = x
            x = cursor2.fetchone()
        conn2.close()
        settings.close()
    if len(last_problem) == 2:
        last_problem = last_problem[0] + last_problem[1]

    url = 'http://codeforces.com/submissions/' + username
    r = requests.get(url)
    max_page = 1
    soup = BeautifulSoup(r.text, "lxml")

    for link in soup.find_all(attrs={"class": "page-index"}):
        s = link.find('a')
        s2 = s.get("href").split('/')
        max_page = max(max_page, int(s2[4]))

    v = False
    r = requests.get('http://codeforces.com/submissions/' + username + '/page/0')
    soup = BeautifulSoup(r.text, "lxml")
    last_try_new = soup.find(attrs={"class": "status-small"})
    last_try_new = str(last_try_new).split()
    last_try_new = str(last_try_new[2]) + str(last_try_new[3])
    for i in range(1, max_page + 1):
        r = requests.get('http://codeforces.com/submissions/' + username + '/page/' + str(i))
        soup = BeautifulSoup(r.text, "lxml")
        count = 0
        j = 0
        ver = soup.find_all(attrs={"class": "submissionVerdictWrapper"})
        last_try = soup.find_all(attrs={"class": "status-small"})
        for link in soup.find_all('a'):
            last_try_date = str(last_try[j]).split()
            last_try_date = str(last_try_date[2]) + str(last_try_date[3])
            if last_try_date == last_update:
                v = True
                break
            s = link.get('href')
            if s != None and s.find('/problemset') != -1:
                s = s.split('/')
                if len(s) == 5:
                    s2 = str(ver[count]).split()
                    s2 = s2[5].split('\"')
                    count += 1
                    j += 1
                    cursor.execute("select * from result where problem = ? and diff = ?", (s[3], s[4]))
                    x = cursor.fetchone()
                    if s2[1] == 'OK' and x != None:
                        cursor.execute("update result set verdict = ? where problem = ? and diff = ?", (s2[1], s[3], s[4]))
                    if x[2] != 'OK':
                        cursor.execute("update result set verdict = ? where problem = ? and diff = ?", (s2[1], s[3], s[4]))
        if v:
            break

    conn.commit()
    conn.close()

    settings = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\settings.db")
    conn = settings.cursor()
    conn.execute("update users set username = ? where chat_id = ?", (str(username), str(chat_id)))
    conn.execute("update users set last_update = ? where chat_id = ?", (str(last_try_new), str(chat_id)))
    conn.execute("update users set last_problem = ? where chat_id = ?", (str(last_problem), str(chat_id)))

    settings.commit()
    settings.close()


def update_theory_base(tag, link):
    theory = sqlite3.connect(os.path.abspath(os.path.dirname(__file__)) + "\\theory.db")
    conn = theory.cursor()
    conn.execute("insert into ? values (?)", (tag, str(link)))
    theory.commit()
    theory.close()