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
            bot.send_message(message.from_user.id, n)
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
                    config.wt = True
                    config.number_day = config.numbers.index(message.text)
                    stt = config.days[config.number_day]
                    bot.send_message(message.from_user.id, "Введите задание! на " + stt)
                else:
                    bot.send_message(message.from_user.id, "not command")
            elif config.wt:
                config.wt = False
                config.wt2 = True
                config.description = message.text
                bot.send_message(message.from_user.id, "Введите время начала этого события:\nВведите час (пишется одной цифрой или числом)")
            elif config.wt2:
                config.wt2 = False
                config.wt3 = True
                print(int(message.text()))
                try:
                    config.d_start = int(message.text())
                except:
                    config.wt2 = True
                    config.wt3 = False
                    bot.send_message(message.from_user.id, "Не корректный ввод, введите заново")
                else:
                    bot.send_message(message.from_user.id, "Теперь введите время окончания")
            elif config.wt3:
                config.wt3 = False
                try:
                    config.d_stop = int(message.text())
                except:
                    config.wt2 = True
                    config.wt3 = False
                    bot.send_message(message.from_user.id, "Не корректный ввод, введите заново")
                else:
                    bot.send_message(message.from_user.id, "Ваше задание принято")


    except:
        print("Warning!")

t1 = potok.Thread(target=mn)
t1.daemon = True
t1.start()

bot.polling(none_stop=True, interval=0)
