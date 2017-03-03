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
    text = text[::-1]
    return text

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
        #text with commands
        @bot.message_handler(content_types=["text"])
        def send_to_text(message):
            try:
                numb = int(message.text)
            except:
                if config.wt:
                    print(plans(message.text)
                else:
                    bot.send_message(message.from_user.id, "Nope, 1 2 3 4 5 6 7")
            else:
                config.number(numb)
                bot.send_message(message.from_user.id, "Вы выбрали " + config.days[numb-1])
        #stop plans
        @bot.message_handler(commands=["stop"])
        def send_to_stop(message):
            print("The user with id: " + str(message.from_user.id) + " use the command SNEW")
            config.wt = False
            bot.send_message(message.from_user.id, "Вы закончили писать задания,\n вы молодец!")
            
	
    except:
        print("Warning!")

t1 = potok.Thread(target=mn)
t1.daemon = True
t1.start()

bot.polling(none_stop=True, interval=0)
