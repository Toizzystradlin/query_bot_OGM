import mysql.connector

def send_message_1(query_id, name, inv, place, cause, msg):  # функция для отправки уведомления о новой заявке мастеру
    import telebot
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor3 = db.cursor(buffered=True)
    sql = "SELECT tg_id FROM employees WHERE (master = True)"
    #sql = "SELECT tg_id FROM employees WHERE (rank = 'инженер')"
    cursor3.execute(sql)
    masters_id = cursor3.fetchall()
    print(masters_id)

    bot_2 = telebot.TeleBot('1044824865:AAGACPaLwqHdOMn5HZamAmSljkoDvSwOiBw')

    keyboard = telebot.types.InlineKeyboardMarkup()
    key_choose = telebot.types.InlineKeyboardButton('Назначить ...', callback_data='choose')
    keyboard.add(key_choose)
    key_postpone = telebot.types.InlineKeyboardButton('Отложить', callback_data='postpone')
    keyboard.add(key_postpone)

    for i in masters_id:
        try:
            bot_2.send_message(i[0], "*НОВАЯ ЗАЯВКА*" + "\n" + "*id_заявки: *" + str(
                query_id) + "\n" + "*Наименование: *" + name + "\n" +
                               "*Инв.№: *" + inv + "\n" + "*Участок: *" + place + "\n" + "*Причина поломки: *" +
                               cause + "\n" + "*Сообщение: *" + msg, reply_markup=keyboard, parse_mode="Markdown")
        except:
            pass

def send_message_5(query_id, name, inv, place, cause, msg, photo):  # функция для отправки уведомления о новой заявке мастеру
    import telebot
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor3 = db.cursor(buffered=True)
    sql = "SELECT tg_id FROM employees WHERE (master = True)"
    #sql = "SELECT tg_id FROM employees WHERE (rank = 'инженер')"
    cursor3.execute(sql)
    masters_id = cursor3.fetchall()
    print(masters_id)

    bot_2 = telebot.TeleBot('1044824865:AAGACPaLwqHdOMn5HZamAmSljkoDvSwOiBw')

    keyboard = telebot.types.InlineKeyboardMarkup()
    key_choose = telebot.types.InlineKeyboardButton('Назначить ...', callback_data='choose')
    keyboard.add(key_choose)
    key_postpone = telebot.types.InlineKeyboardButton('Отложить', callback_data='postpone')
    keyboard.add(key_postpone)
    for i in masters_id:
        try:
            bot_2.send_photo(i[0], open(photo, 'rb'))
            bot_2.send_message(i[0], "*НОВАЯ ЗАЯВКА*" + "\n" + "*id_заявки: *" + str(
                query_id) + "\n" + "*Наименование: *" + name + "\n" +
                               "*Инв.№: *" + inv + "\n" + "*Участок: *" + place + "\n" + "*Причина поломки: *" +
                               cause + "\n" + "*Сообщение: *" + msg, reply_markup=keyboard, parse_mode="Markdown")
        except:
            pass