token = "362521239:AAE3wv5PLZ-BuntbSIIizAH40mLOYbfbfWo"
days = ["понедельник","вторник","среда","четверг","пятница","суббота","воскресенье"]
numbers = ["1","2", "3", "4", "5", "6", "7"]

wt = False
number = 0
start = 0
stop = 0
url = "/home/pi/projects/python3/asistent_bot/st.db"
date_number = 5
week_none = False
write_plans = """
Введите ваши планы в таком формате:
Сначала пишете ваши великие планы...
На предпоследней строке пишете время начала задания;
На последней - время конца задания;

Время пишете одной цифрой или числом;
"""

write_more = """
\nВаше задание записано

Хотите написать что-то ещё?
Если да, то просто продалжайте писать задания в таком же формате,
Если нет, то выполните команду /snew!
"""
