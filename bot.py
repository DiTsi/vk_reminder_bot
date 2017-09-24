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
from dateutil.relativedelta import relativedelta

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
    'д': 'd', 'Д': 'd', 'ч': 'd', 'Ч': 'd'
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
            return d.replace(month=(d.month + 1), day=day, hour=hours, minute=minutes, second=0)


def return_list_of_uids_and_messages(messages_list):
    ids_list = list()
    mes_list = list()

    for i in messages_list:
        ids_list.append(i['body'])
        mes_list.append(i['uid'])
    return {'uid': ids_list, 'messages': mes_list}



def get_user_gmt_shift(user_id):
    #!
    return 3


def replace_time(datetime, hours0, minutes0):
    return datetime.replace(hour=hours0, minute=minutes0)


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


    # while True:
    datenow = datetime.utcnow()
    list_of_unread_messages = get_unread_messages(api)
    list_of_messages_objects = [Message(i) for i in list_of_unread_messages]

    for message in list_of_messages_objects:

        # print(message.date)
        print(message.message)
        try:
            [mes, shift, days, hours, minutes] = message_parser(message.message)
        except ValueError:
            # HANDLER FOR UNSUPPORTED MESSAGES
            print('не могу обработать сообщение: ' + message.message)
            print('\n')

        else:
            if shift == '+':
                # HANDLER FOR MESSAGE WITH +
                print('message.date = ' + message.date)
                print('message.delay:')
                # print('hours')
                time_delta = timedelta(hours=hours, minutes=minutes)
                print(objtime2strtime(strtime2objtime(message.date) + time_delta))
                # send_notification.apply_async(([message.user_id, mes], eta=message.date+))

            else:
                # HANDLER FOR OTHER MESSAGES
                user_gmt_shift = get_user_gmt_shift(message.user_id)
                message_datetime = strtime2objtime(message.date) + timedelta(hours=(user_gmt_shift - server_gmt_shift))
                print('message_datetime = ' + objtime2strtime(message_datetime))

                # CODE TO CHANGE DAY
                if shift == '':
                    shift_day = '+0'
                else:
                    shift_day = shift_selector[shift]

                notification_datetime = datetime

                if isinstance(shift_day, int):
                    if not notification_time_in_future(message_datetime, next_weekday(message_datetime, shift_day).replace(hour=hours, minute=minutes, second=0)):
                        notification_datetime = message_datetime + timedelta(days=7)
                        notification_datetime.replace(hour=hours, minute=minutes, second=0)
                    else:
                        notification_datetime = next_weekday(message_datetime, shift_day).replace(hour=hours, minute=minutes, second=0)

                else:
                    try:
                        notification_datetime = message_datetime.replace(hour=hours, minute=minutes, second=0)
                    except ValueError:
                        #!
                        print('время таким не бывает!')
                        # stop script
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
                                #! неправильно задана дата
                                print('число таким не бывает')
                            else:
                                notification_datetime = next_day(notification_datetime, days, hours, minutes)
                        else:
                            # shift_day = int(shift_day)
                            print('check code!')
                            exit(1)
                print('сообщение будет доставлено: ' + str(notification_datetime))

            print('\n')

main()