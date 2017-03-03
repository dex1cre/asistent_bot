#!/usr/bin/python3
#!usr/bin python3
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
#constant
import string

bot = tlb.TeleBot(config.token)

def pr_mn(tk):
    con = sqlite3.connect(config.url)
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

def plans(text):
    first = 0
    second = 0
    text = text[::-1]
    #first symbol is number?
    try:
        first = int(text[0])
    except:
        return False
    else:
        #try to get second number
        st = ""
        for i in text:
            try:
                g = int(i)
            except:
                if i == "\n":
                    second = int(st[::-1])
                    st = ""
                    ind = text.index(i) + 1
                    for i in range(ind, len(text)):
                        try:
                            g = int(text[i])
                        except:
                            if st != "":
                                first = int(st[::-1])
                                return (first, second)
                            else:
                                return False
                        else:
                            print(text[i])
                            st = st + text[i]
                else:
                    return False
            else:
                print("hello")
                st = st + i
                            
def mn():
    try:
        @bot.message_handler(commands=["start"])
        def send_to_start(message):
            if pr_mn(message.from_user.id) == "good":
                print(message.from_user.id, "перезапустил сессию")
            else:
                print(message.from_user.id, "создал первую сессию")
                con = sqlite3.connect(config.url)
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
            um.row("/new", "/snew", "/week")
            bot.send_message(message.from_user.id, "Начнём!", reply_markup=um)

        #Завершение сессии
        @bot.message_handler(commands=["stop"])
        def send_to_stop(message):
            config.wt = False
            hm = tlb.types.ReplyKeyboardRemove()
            bot.send_message(message.from_user.id, "До встречи!", reply_markup=hm)

        #what's now?
        @bot.message_handler(commands=["now"])
        def send_to_stop(message):
            print("The user with id: " + str(message.from_user.id) + " use the command NOW")
            hm = tlb.types.ReplyKeyboardRemove()
            bot.send_message(message.from_user.id, "Now hello")

        #new
        @bot.message_handler(commands=["new"])
        def send_to_new(message):
            config.wt = True
            print("The user with id: " + str(message.from_user.id) + " use the command NEW")
            st = "Чтобы добавить новые задачи напишите номер дня недели от 1 до 7"
            bot.send_message(message.from_user.id, st)

        #stop plans
        @bot.message_handler(commands=["snew"])
        def send_to_stop(message):
            print("The user with id: " + str(message.from_user.id) + " use the command SNEW")
            config.wt = False
            bot.send_message(message.from_user.id, "Вы закончили писать задания,\n вы молодец!")
        
        #text with commands
        @bot.message_handler(content_types=["text"])
        def send_to_text(message):
            if config.wt and message.text in config.numbers:
                config.number = int(message.text)
                bot.send_message(message.from_user.id, "Вы выбрали " + config.days[int(message.text)-1])
            elif config.wt:
                bl = plans(message.text)
                tp = type(bl)
                if tp == tuple:
                    idd = message.from_user.id
                    text = message.text
                    start = bl[0]
                    stop = bl[1]
                    ms = text[:len(text)-3]
                    con = sqlite3.connect(config.url)
                    cur = con.cursor()
                    number = config.number-1
                    st = (ms, idd, start, stop, number)
                    sql = "INSERT INTO plans(what, id_user, dtime_start, dtime_stop, id_day) VALUES(?, ?, ?, ?, ?)"
                    try:
                        cur.execute(sql, st)
                    except sqlite3.DatabaseError as err:
                        print(err)
                    else:
                        con.commit()
                        bot.send_message(message.from_user.id, "Ваше задание:\n" + ms + "\nзагружено!")
                elif tp == bool and not bl:
                    bot.send_message(message.from_user.id, "Что-то с вашим заданием не так! Проверьте, правильно ли вы вводите время начала и конца!")
            else:
                bot.send_message(message.from_user.id, "Nope, 1 2 3 4 5 6 7")
            
	
    except:
        print("Warning!")

t1 = potok.Thread(target=mn)
t1.daemon = True
t1.start()

bot.polling(none_stop=True, interval=0)
