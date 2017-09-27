#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import vk
import re
from tasks import send_notification
from datetime import datetime, timedelta
# import logging
# from dateutil.relativedelta import relativedelta
from parser import message_parser, parse_1
import socket
# import configparser

import database
from config_parser import get_string
# from dateutil.relativedelta import relativedelta



REMOTE_SERVER = "www.google.com"





token = <token>
count = 10  # How many messages must be readed (max - 200)
server_gmt_shift = 3


shift_selector = {
    'пн': 0, 'пон': 0, 'понед': 0, 'понедельник': 0,
    'вт': 1, 'вторн': 1, 'вторник': 1,
    'ср': 2, 'сред': 2, 'среда': 2,
    'чт': 3, 'четв': 3, 'четверг': 3,
    'пят': 4, 'пятн': 4, 'пятниц': 4, 'пятница': 4,
    'сб': 5, 'суб': 5, 'суббот': 5, 'суббота': 5,
    'вс': 6, 'вос': 6, 'воскр': 6, 'воскрес': 6, 'воскресенье': 6,
    'з': '+1', 'завтра': '+1', 'с': '+0', 'сегодня': '+0', 'пз': '+2', 'послезавтра': '+2',
    '+': '+',
    'д': 'd', 'Д': 'd'
}

# selector_day = []

timeformat = '%Y.%m.%d_%H:%M:%S'


class Message:
    # message = str()
    # message_id = int()
    # date = datetime
    # user_id = int()

    def __init__(self, message):
        self.message = message['body']
        self.message_id = message['mid']
        self.date = datetime.fromtimestamp(message['date']).strftime(timeformat)
        self.user_id = message['uid']

    def __str__(self):
        return self.message


def is_connected():
    try:
        host = socket.gethostbyname(REMOTE_SERVER)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False


def strtime2objtime(string_utc):
    return datetime.strptime(string_utc, timeformat)


def objtime2strtime(timeobject):
    return timeobject.strftime(timeformat)



def get_unread_messages(api):
    try:
        messages = api.messages.get(count=count)
    except Exception:
        return []
    del messages[0]
    unread_messages_list = list()

    # GET UNREAD LIST
    for i in messages:
        if i['read_state'] == 0:
            unread_messages_list.append(i)

    return unread_messages_list


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead < 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days=days_ahead)


def mydebug(message, notif_eta, user_tz):
    print('     user_tz = ' + str(user_tz))
    print('message.text = ' + message.message)
    print('message.date = ' + message.date + '(server time)')
    print('   send.date = ' + objtime2strtime(notif_eta + timedelta(hours=server_gmt_shift)) + '(server time)')


def next_day(d, day, hours, minutes):
    days_ahead = day - d.day
    if days_ahead < 0:
            return d.replace(month=d.month + 1, day=day, hour=hours, minute=minutes, second=0)
    elif days_ahead == 0:
        if notification_time_in_future(d, d.replace(day=day, hour=hours, minute=minutes, second=0)):
            return d.replace(hour=hours, minute=minutes, second=0, day=day)
        else:
            return day.replace(month=(d.month + 1), hour=hours, minute=minutes, second=0)

    else:
        try:
            return d.replace(day=day, hour=hours, minute=minutes, second=0)
        except ValueError:
            try:
                return d.replace(month=(d.month + 1), day=day, hour=hours, minute=minutes, second=0)
            except ValueError:
                return d.replace(month=(d.month + 2), day=day, hour=hours, minute=minutes, second=0)


def return_list_of_uids_and_messages(messages_list):
    ids_list = list()
    mes_list = list()

    for i in messages_list:
        ids_list.append(i['body'])
        mes_list.append(i['uid'])
    return {'uid': ids_list, 'messages': mes_list}



def get_user_gmt_shift(user_id):
    return database.db_search(user_id)["data"]


def replace_time(datetime, hours0, minutes0):
    return datetime.replace(hour=hours0, minute=minutes0)


def make_eta(datetime, user_gmt):
    return (datetime - timedelta(hours=user_gmt))


def notification_time_in_future(message_datetime, notification_datetime):
    if notification_datetime < message_datetime:
        return False
    else:
        return True


def main():
    if not is_connected():
        #!
        print('no internet access')
        exit(0)

    api = vk.API(vk.Session(access_token=token))


    while True:
        # datenow = datetime.utcnow()
        list_of_unread_messages = get_unread_messages(api)
        list_of_messages_objects = [Message(i) for i in list_of_unread_messages]

        for message in list_of_messages_objects:

            ret = re.compile(r'^[Gg][+-](?P<timezone>[0-9]{1,2})$')
            mat = ret.match(message.message)
            if mat:
                database.db_add(str(message.user_id), str(mat.group('timezone')))
                send_notification.delay(message.user_id, get_string('strings', 'success_added_gmt'))
                continue

            if not database.db_search(message.user_id):
                send_notification.delay(message.user_id, get_string('strings', 'not_in_database'))
                continue

            user_tz = get_user_gmt_shift(message.user_id)

            # print(message.date)
            print()
            try:
                [mes, shift, days, hours, minutes] = message_parser(message.message)
            except ValueError:
                # HANDLER FOR UNSUPPORTED MESSAGES
                send_notification.delay(message.user_id, get_string('strings', 'format_error') + '\n' + get_string('strings', 'examples'))
                # print()

            else:
                if mes == '':
                    mes = get_string('strings', 'empty_message')
                if shift == '+':
                    # HANDLER FOR MESSAGE WITH +
                    time_delta = timedelta(hours=hours, minutes=minutes)
                    send_time = strtime2objtime(message.date) - timedelta(hours=server_gmt_shift) + time_delta
                    send_notification.delay([message.user_id], get_string('strings', 'task_added') + ' ' + objtime2strtime(make_eta(send_time, -user_tz)))
                    send_notification.apply_async(([message.user_id], mes), eta=make_eta(send_time, 0))
                    mydebug(message, send_time, user_tz)
                    continue

                # HANDLER FOR OTHER MESSAGES
                message_datetime = strtime2objtime(message.date) + timedelta(hours=(user_tz - server_gmt_shift))

                if shift == '':
                    shift_day = '+0'
                else:
                    try:
                        shift_day = shift_selector[shift]
                    except KeyError:
                        send_notification.delay(message.user_id, get_string('strings', 'format_error') + '\n' + get_string('strings', 'examples'))
                        continue


                if isinstance(shift_day, int):
                    if not notification_time_in_future(message_datetime, next_weekday(message_datetime, shift_day).replace(hour=hours, minute=minutes, second=0)):
                        notification_datetime = message_datetime + timedelta(days=7)
                        notification_datetime.replace(hour=hours, minute=minutes, second=0)
                    else:
                        notification_datetime = next_weekday(message_datetime, shift_day).replace(hour=hours, minute=minutes, second=0)

                    eta = make_eta(notification_datetime, user_tz)
                    send_notification.delay([message.user_id], get_string('strings', 'task_added') + ' ' + objtime2strtime(eta + timedelta(hours=user_tz)))
                    send_notification.apply_async(([message.user_id], mes), eta=eta)
                    mydebug(message, eta, user_tz)


                else:
                    try:
                        notification_datetime = message_datetime.replace(hour=hours, minute=minutes, second=0)
                    except ValueError:
                        send_notification.delay([message.user_id], get_string('strings', 'incorrect_time_format'))

                        continue
                    else:
                        if shift_day == '+0':
                            if not notification_time_in_future(message_datetime, notification_datetime):
                                shift_day = '+1'
                        if shift_day == '+1':
                            notification_datetime += timedelta(days=1)
                        elif shift_day == '+2':
                            notification_datetime += timedelta(days=2)

                        elif shift_day == 'd':
                            if not 1 <= days <= 31:
                                send_notification.delay(([message.user_id], get_string('strings', 'incorrect_day')))
                                continue
                            else:
                                notification_datetime = next_day(notification_datetime, days, hours, minutes)
                        send_notification.delay([message.user_id],get_string('strings', 'task_added') + ' ' + objtime2strtime(make_eta(notification_datetime, 0)))
                        send_notification.apply_async(([message.user_id], mes), eta=make_eta(notification_datetime, user_tz))
                        mydebug(message, notification_datetime - timedelta(hours=user_tz), user_tz)

        # print('database = ')
        # database.db_show()
        time.sleep(1)


main()
