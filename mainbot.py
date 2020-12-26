from datetime import datetime
import mysql.connector
import telebot
from telebot import apihelper
import Send_message

query_photo_path = 'C:/Users/User/Desktop/projects/DjangoOGM/main/static/images/query_photos/'

#while True:
try:
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor = db.cursor(True)
    user_dict = {}
    bot = telebot.TeleBot('1048146486:AAGwY0ClpWvUtjlBy-D6foxhIntZUFb7-5s')
    class Q:
        def __init__(self, chat):
            self.chat_id = chat
            self.eq_id = None
            self.invnum = None
            self.eq_name = None
            self.eq_type = None
            self.area = None
            self.eq_status = None
            self.reason = None
            self.msg = None
            self.query_status = None
            self.query_id = None
            self.doers = None
            self.photo_name = None
            self.creator_tg_id = None
    @bot.message_handler(commands=['start', 'check', 'new'])
    def handle_commands(message):
        # обрабатывает запуск с параметром (гиперссылку где прописан параметр start)
        if message.text.startswith('/start'):
            try:
                if len(message.text.split()) > 1:
                    ref = message.text.split()
                    REFINT = str(ref[1])
                    sql = "SELECT * from equipment WHERE (eq_id = %s)"
                    val = (REFINT,)
                    cursor.execute(sql, val)
                    Machine = cursor.fetchone()
                    bot.send_message(message.chat.id, "*Наименование: *" + Machine[2] + "\n" + "*Инв.№: *" +
                                     Machine[1] + "\n" + "*Тип станка: *" + Machine[3] + "\n" + "*Участок: *" + Machine[4],
                                     parse_mode="Markdown")
                    print(message.message_id)
                    chat_id = message.chat.id
                    query = Q(chat_id)
                    query.eq_id = Machine[0]
                    query.invnum = Machine[1]
                    query.eq_name = Machine[2]
                    query.eq_type = Machine[3]
                    query.area = Machine[4]
                    query.creator_tg_id = chat_id
                    user_dict[chat_id] = query
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    key_1 = telebot.types.InlineKeyboardButton('Да', callback_data='stopped')
                    keyboard.add(key_1)
                    key_2 = telebot.types.InlineKeyboardButton('Нет', callback_data='working')
                    keyboard.add(key_2)
                    bot.send_message(message.chat.id, 'Оборудование остановилось?', reply_markup=keyboard)
                else:
                    bot.send_message(message.chat.id, 'ты просто написал старт')
            except Exception as ex:
                print(ex)
        if message.text == '/check':
            try:
                bot.send_message(message.chat.id, 'Привет, да я работаю')
            except:
                print('ошибка в чек')
        if message.text == '/new':
            try:
                cursor.execute('SELECT area FROM areas')
                areas = cursor.fetchall()
                keyboard = telebot.types.InlineKeyboardMarkup()
                for i, area in enumerate(areas):
                    key = telebot.types.InlineKeyboardButton(area[0], callback_data=area[0])
                    keyboard.add(key)
                bot.send_message(message.chat.id, 'Выберите участок', reply_markup=keyboard)
            except Exception as ex:
                print(ex)
    @bot.callback_query_handler(func=lambda call: True)
    def callback_worker(call):
        sql = "SELECT reason FROM reasons"
        cursor.execute(sql)
        reasons = cursor.fetchall()
        for i in reasons:
            if call.data == i[0]:
                chat_id = call.message.chat.id
                query = user_dict[chat_id]
                query.reason = i[0]
                bot.send_message(call.message.chat.id, "*Наименование: *" + query.eq_name +
                                 "\n" + "*Инв.№: *" + query.invnum + "\n" + "*Тип станка: *" + query.eq_type + "\n" + "*Участок: *" +
                                 query.area + "\n" + "*Оборудование остановилось?: *" + query.eq_status + "\n" +
                                 "*Причина поломки: *" + query.reason, parse_mode="Markdown")
                try:
                    bot.delete_message(call.message.chat.id, message_id=call.message.message_id - 1)
                    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                except:
                    print('не получилось удалить сообщения')
                msg = bot.send_message(call.message.chat.id, 'Введите описание проблемы')
                bot.register_next_step_handler(msg, sendquery2)
        if call.data == 'send_query':
            try:
                q_status = ''
                chat_id = call.message.chat.id
                query = user_dict[chat_id]
                query.query_status = 'Новая'
                sql = "INSERT INTO queries (eq_id, reason, msg, post_time, " \
                      "query_status, json_emp, creator_tg_id) VALUES (" \
                      "%s, %s, %s, %s, %s, %s, %s) "
                val = [
                    (query.eq_id, query.reason, query.msg, datetime.now(),
                     query.query_status, '{"doers": []}', query.creator_tg_id)
                ]
                cursor.executemany(sql, val)
                db.commit()
                sql = "UPDATE equipment SET eq_status = %s WHERE eq_id = %s"
                val = (query.eq_status, query.eq_id)
                cursor.execute(sql, val)
                db.commit()
                if query.eq_status == 'Остановлено':
                    sql = "SELECT * FROM eq_stoptime WHERE (eq_id = %s) AND (start_time IS NULL) ORDER BY id DESC LIMIT 1"
                    val = (query.eq_id,)
                    cursor.execute(sql, val)
                    result = cursor.fetchall()
                    result = list(result)
                    if len(result) == 0:
                        sql = "INSERT INTO eq_stoptime (eq_id, stop_time) VALUES (%s, %s)"
                        val = (query.eq_id, datetime.now())
                        cursor.execute(sql, val)
                        db.commit()
                    q_status = 'Остановлено'
                elif query.eq_status == 'Работает':
                    sql = "SELECT * FROM eq_stoptime WHERE (eq_id = %s) AND (start_time IS NULL) ORDER BY id DESC LIMIT 1"
                    val = (query.eq_id,)
                    cursor.execute(sql, val)
                    result = cursor.fetchone()
                    q_status = 'Работает'
                    try:
                        result = list(result)
                        if len(result) > 0:
                            i = result[0]
                            sql = "UPDATE eq_stoptime SET start_time = %s WHERE id = %s"
                            val = (datetime.now(), i)
                            cursor.execute(sql, val)
                            db.commit()
                    except: pass
                sql = "SELECT MAX(query_id) FROM queries"
                cursor.execute(sql)
                query.query_id = cursor.fetchone()[0]
                bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                bot.send_message(call.message.chat.id, 'Заявка отправлена')
                # Отправить уведомление мастеру
                Send_message.send_message_1(query.query_id, query.eq_name, query.invnum, query.area, query.reason,
                                            query.msg, query.creator_tg_id, q_status)  # Отправить уведомление мастерам
            except Exception as ex:
                print(ex)
        elif call.data == 'add_photo':
            try:
                #bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                #bot.send_message(call.message.chat.id, 'Заявка отменена')
                msg = bot.send_message(call.message.chat.id, 'Отправте мне фото')
                bot.register_next_step_handler(msg, handle__photo)
                bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
            except:
                print('ошибка в add_photo')
        elif call.data == 'stopped':
            try:
                chat_id = call.message.chat.id
                query = user_dict[chat_id]
                query.eq_status = 'Остановлено'
                bot.send_message(call.message.chat.id, "*Наименование: *" + query.eq_name +
                                 "\n" + "*Инв.№: *" + query.invnum + "\n" + "*Тип станка: *" + query.eq_type + "\n" + "*Участок: *" +
                                 query.area + "\n" + "*Оборудование остановилось?: *" + query.eq_status,
                                 parse_mode="Markdown")
                try:
                    bot.delete_message(call.message.chat.id, message_id=call.message.message_id - 1)
                    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                except:
                    print('не получилось удалить сообщения')
                reason(call)
            except:
                print('ошибка в стопед')
        elif call.data == 'working':
            try:
                chat_id = call.message.chat.id
                query = user_dict[chat_id]
                query.eq_status = 'Работает'
                bot.send_message(call.message.chat.id, "*Наименование: *" + query.eq_name +
                                 "\n" + "*Инв.№: *" + query.invnum + "\n" + "*Тип станка: *" + query.eq_type + "\n" + "*Участок: *" +
                                 query.area + "\n" + "*Оборудование остановилось?: *" + query.eq_status,
                                 parse_mode="Markdown")
                try:
                    bot.delete_message(call.message.chat.id, message_id=call.message.message_id - 1)
                    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                except:
                    print('не получилось удалить сообщение')
                reason(call)
            except:
                print('ошибка в воркинг')
        cursor.execute('SELECT area FROM areas')
        areas = cursor.fetchall()
        for area in areas:
            if call.data == area[0]:
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except: print('Ошибка в удалении сообщений')
                try:
                    cursor.execute("SELECT * from equipment WHERE eq_name = 'Другое' AND area = %s", [area[0]])
                    Machine = cursor.fetchone()
                    bot.send_message(call.message.chat.id, "*Наименование: *" + Machine[2] + "\n" + "*Инв.№: *" +
                                     Machine[1] + "\n" + "*Тип станка: *" + Machine[3] + "\n" + "*Участок: *" + Machine[
                                         4],
                                     parse_mode="Markdown")
                    print(call.message.message_id)
                    chat_id = call.message.chat.id
                    query = Q(chat_id)
                    query.eq_id = Machine[0]
                    query.invnum = Machine[1]
                    query.eq_name = Machine[2]
                    query.eq_type = Machine[3]
                    query.area = Machine[4]
                    user_dict[chat_id] = query
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    key_1 = telebot.types.InlineKeyboardButton('Да', callback_data='stopped')
                    keyboard.add(key_1)
                    key_2 = telebot.types.InlineKeyboardButton('Нет', callback_data='working')
                    keyboard.add(key_2)
                    bot.send_message(call.message.chat.id, 'Оборудование остановилось?', reply_markup=keyboard)
                except Exception as ex:
                    print(ex)
    def reason(call):
        try:
            # выводим кнопки для выбора причины поломки
            sql = "SELECT reason FROM reasons"
            cursor.execute(sql)
            reasons = cursor.fetchall()
            keyboard_reasons = telebot.types.InlineKeyboardMarkup()
            for i in reasons:
               # keyboard = telebot.types.InlineKeyboardMarkup()
                key = telebot.types.InlineKeyboardButton(i[0], callback_data=i[0])
                keyboard_reasons.add(key)
            bot.send_message(call.message.chat.id, 'Выберите тип поломки', reply_markup=keyboard_reasons)
        except:
            print('ошибка в риазон')
    def sendquery1(message):
        try:
            chat_id = message.chat.id
            query = user_dict[chat_id]
            query.msg = message.text
            print(message.message_id)
            print(message.chat.id)
            print(message.text)
            try:
                bot.delete_message(message.chat.id, message_id=message.message_id - 2)
                bot.delete_message(message.chat.id, message_id=message.message_id - 1)
            except:
                print('не получилось удалить сообщения')
            bot.send_message(message.chat.id, "*Наименование: *" + query.eq_name +
                             "\n" + "*Инв.№: *" + query.invnum + "\n" + "*Тип станка: *" + query.eq_type + "\n" + "*Участок: *" +
                             query.area + "\n" + "*Причина поломки: *" + query.reason +
                             "\n" + "*Сообщение:*" + query.msg, parse_mode="Markdown")
            keyboard = telebot.types.InlineKeyboardMarkup()
            key_yes = telebot.types.InlineKeyboardButton('Отправить', callback_data='send_query')
            keyboard.add(key_yes)
            key_no = telebot.types.InlineKeyboardButton('Отмена', callback_data='cancel_query')
            keyboard.add(key_no)
            bot.send_message(message.chat.id, "Отправить заявку?", reply_markup=keyboard)
        except:
            print('ошибка в сендкваери')
    def sendquery2(message):
        chat_id = message.chat.id
        query = user_dict[chat_id]
        query.msg = message.text
        print(message.message_id)
        print(message.chat.id)
        print(message.text)
        #try:
        #    bot.delete_message(message.chat.id, message_id=message.message_id - 2)
        #    bot.delete_message(message.chat.id, message_id=message.message_id - 1)
        #except:
            #print('не получилось удалить сообщения')
        bot.send_message(message.chat.id, "*Наименование: *" + query.eq_name +
                         "\n" + "*Инв.№: *" + query.invnum + "\n" + "*Тип станка: *" + query.eq_type + "\n" + "*Участок: *" +
                         query.area + "\n" + "*Причина поломки: *" + query.reason +
                         "\n" + "*Сообщение:*" + query.msg, parse_mode="Markdown")
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_yes = telebot.types.InlineKeyboardButton('Отправить без фото', callback_data='send_query')
        keyboard.add(key_yes)
        key_no = telebot.types.InlineKeyboardButton('Добавить фото', callback_data='add_photo')
        keyboard.add(key_no)
        bot.send_message(message.chat.id, "Добавить фото?", reply_markup=keyboard)
    def handle__photo(message):
        q_status = ''
        chat_id = message.chat.id
        query = user_dict[chat_id]
        try:
            print('message.photo =', message.photo)
            fileID = message.photo[-1].file_id
            print('fileID =', fileID)
            file_info = bot.get_file(fileID)
            print('file.file_path =', file_info.file_path)
            downloaded_file = bot.download_file(file_info.file_path)
            query.photo_name = file_info.file_path
            with open(query_photo_path + file_info.file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
        except Exception as e:
            print(e)
        try:
            chat_id = message.chat.id
            query = user_dict[chat_id]
            query.query_status = 'Новая'
            sql = "INSERT INTO queries (eq_id, reason, msg, post_time, " \
                  "query_status, json_emp, photo_name, creator_tg_id) VALUES (" \
                  "%s, %s, %s, %s, %s, %s, %s, %s) "
            val = [
                (query.eq_id, query.reason, query.msg, datetime.now(),
                 query.query_status, '{"doers": []}', query.photo_name, query.creator_tg_id)
            ]
            cursor.executemany(sql, val)
            db.commit()
            sql = "UPDATE equipment SET eq_status = %s WHERE eq_id = %s"
            val = (query.eq_status, query.eq_id)
            cursor.execute(sql, val)
            db.commit()
            if query.eq_status == 'Остановлено':
                sql = "SELECT * FROM eq_stoptime WHERE (eq_id = %s) AND (start_time IS NULL) ORDER BY id DESC LIMIT 1"
                val = (query.eq_id,)
                cursor.execute(sql, val)
                result = cursor.fetchall()
                result = list(result)
                if len(result) == 0:
                    sql = "INSERT INTO eq_stoptime (eq_id, stop_time) VALUES (%s, %s)"
                    val = (query.eq_id, datetime.now())
                    cursor.execute(sql, val)
                    db.commit()
                q_status = 'Остановлено'
            elif query.eq_status == 'Работает':
                sql = "SELECT * FROM eq_stoptime WHERE (eq_id = %s) AND (start_time IS NULL) ORDER BY id DESC LIMIT 1"
                val = (query.eq_id,)
                cursor.execute(sql, val)
                result = cursor.fetchone()
                q_status = 'Работает'
                try:
                    result = list(result)
                    if len(result) > 0:
                        i = result[0]
                        sql = "UPDATE eq_stoptime SET start_time = %s WHERE id = %s"
                        val = (datetime.now(), i)
                        cursor.execute(sql, val)
                        db.commit()
                except:
                    pass
            sql = "SELECT MAX(query_id) FROM queries"
            cursor.execute(sql)
            query.query_id = cursor.fetchone()[0]
            #bot.delete_message(message.chat.id, message_id=message.message_id)
            bot.send_message(message.chat.id, 'Заявка отправлена')
            # Отправить уведомление мастеру
            Send_message.send_message_5(query.query_id, query.eq_name, query.invnum, query.area, query.reason,
                                        query.msg, query_photo_path + query.photo_name, query.creator_tg_id, q_status)  # Отправить уведомление мастерам
        except Exception as ex:
            print(ex)


    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
except: pass
