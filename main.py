#-*- coding: utf-8 -*-

#главный(здесь) модуль для работы с telegram
import telebot as tlb
#модуль для определения дня недели
from datetime import datetime
#модуль для многопоточности
import threading as potok
#модуль для работы с базами данных sqlite3
import sqlite3
#модуль с основными константами
import config

bot = tlb.TeleBot(config.token)

def pr_mn(tk):
    con = sqlite3.connect("st.db")
    cur = con.cursor()
    sql = "SELECT * FROM users WHERE id_user=" + str(tk)
    try:
        st = cur.execute(sql)
    except sqlite3.DatabaseError as err:
        print("Ошибка: " + err)
    else:
        try:
            st = st.fetchone()
            t = st[1]
        except:
            return "bad"
        else:
            return "good"
    cur.close()
    con.close()

def mn():
    try:
        @bot.message_handler(commands=["start"])
        def send_to_start(message):
            if pr_mn(message.from_user.id) == "good":
                print(message.from_user.id, "перезапустил сессию")
            else:
                print(message.from_user.id, "создал первую сессию")
                con = sqlite3.connect("st.db")
                cur = con.cursor()
                sql = "INSERT INTO users(id_user) VALUES('" + str(message.from_user.id) + "')"
                try:
                    cur.execute(sql)
                except sqlite3.DatabaseError as err:
                    print("Ошибка ", err)
                else:
                    print(message.from_user.id, " добавлен в базу данных")
                    con.commit()
                cur.close()
                con.close()

            um = tlb.types.ReplyKeyboardMarkup(True)
            um.row("/start", "/now", "/stop")
            um.row("/new", "/today", "/week")
            bot.send_message(message.from_user.id, "Начнём!", reply_markup=um)

        #Завершение сессии
        @bot.message_handler(commands=["stop"])
        def send_to_stop(message):
            hm = tlb.types.ReplyKeyboardRemove()
            bot.send_message(message.from_user.id, "До встречи!", reply_markup=hm)

        #Другие команды
        #команда для просмотра задачи в данный момент времени
        @bot.message_handler(commands=["now"])
        def send_to_now(message):
            n = datetime.weekday(datetime.now())
            con = sqlite3.connect("st.db")
            cur = con.cursor()
            sql = "SELECT * FROM users WHERE id_user="+ str(message.from_user.id)
            id = cur.execute(sql).fetchone()[0]
            cur.close()

            cur = con.cursor()
            sql = "SELECT * FROM plans WHERE id_user=" + str(id) + " AND id_day=" + str(n)
            cur.execute(sql)
            st = ""
            for i in cur.fetchall():
                st = st + "\nЗадание: " + str(i[1]) + "\nВремя выполнения: " + str(i[3]) + "-" + str(i[4]) + "\n"
            cur.close()
            con.close()
            bot.send_message(message.from_user.id, st)
        #команда для создания новых задач
        @bot.message_handler(commands=["new"])
        def send_to_new(message):
            st = """
Выберите день недели\n
/0 - понедельник
/1 - вторник
/2 - среда
/3 - четверг
/4 - пятница
/5 - суббота
/6 - воскресенье
"""
            bot.send_message(message.from_user.id, st)
        #команда для обработки дней недели
        @bot.message_handler(content_types=['text'])
        def repeat_all_messages(message):
            if "/" in message.text:
                if message.text in config.numbers:
                    config.number = config.numbers.index(message.text)
                    stt = config.days[config.number]
                    st = """
Введите задание на """ + stt + """
Сначала введите само задание
Потом введите время начала задания
Потом - время конца задания

Каждый пункт нужно писать через Enter, то есть переностить на новую строчку!!!
"""
                    config.wt = True
                    bot.send_message(message.from_user.id, st)
                else:
                    bot.send_message(message.from_user.id, "not command")
            elif config.wt:
                stt = ""
                x = []
                in_n = 0
                ms_text = message.text + "\n"
                for i in ms_text:
                    if i != "\n":
                        stt = stt + i
                    else:
                        in_n += 1
                        x.append(stt)
                        stt = ""
                if in_n < 3:
                    bot.send_message(message.from_user.id, "Вы что-то ввели не так, попробуйте ещё раз")
                else:
                    con = sqlite3.connect("st.db")
                    cur = con.cursor()
                    sql = "SELECT * FROM users WHERE id_user=" + str(message.from_user.id)
                    t = con.execute(sql)
                    t = t.fetchone()
                    id = t[0]
                    print(config.number)
                    t = (x[0], id, x[1], x[2], config.number)
                    sql = "INSERT INTO plans(what, id_user, dtime_start, dtime_stop, id_day) VALUES(?,?,?,?,?)"
                    cur.execute(sql, t)
                    con.commit()
                    cur.close()
                    con.close()
                    config.number = 0
                    config.wt = False
                    stt = "Ваше задание: " + x[0] + "\nНачало работы " + x[1] + "\nКонец работы: " + x[2] + "\nЗадание записано!"
                    bot.send_message(message.from_user.id, stt)
            else:
                bot.send_message(message.from_user.id, "Я пока что не могу отвечать на подобные вопросы! Простите")


    except:
        print("Warning!")

t1 = potok.Thread(target=mn)
t1.daemon = True
t1.start()

bot.polling(none_stop=True, interval=0)
