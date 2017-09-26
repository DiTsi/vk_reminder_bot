# -*- coding: utf-8 -*-

import pyparsing as pp
import datetime
import re

rus_alphas = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
message_symbols = '!"@#$%^&*();:.,/\\|'

#     Or('пн' | 'пон' | 'понед' | 'понедельник' | 'вт' | 'вторн' | 'вторник' | 'ср' | 'сред' | 'среда' | 'чт' | 'четв' | 'четверг' | 'пят' | 'пятн' | 'пятниц' | 'пятница' | 'сб' | 'суб' | 'суббот' | 'суббота' | 'вс' | 'вос' | 'воскр' | 'воскрес' | 'воскресенье' | 'з' | 'завтра' | 'с' | 'сегодня' | 'пз' | 'послезавтра')
# )('pretime')

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

def parse_1(text):
    regex = re.compile('^(?P<message>[\s\S]*[\s])?(?P<time>[\S]+)[\s]*$')
    try:
        result = regex.match(text)
        message = result.group('message')
        if message == None:
            message = ''
        time = result.group('time')
    except:
        return -1
    return {'message': message, 'time': time}


def assign(parse_dict, key):
    if key in parse_dict.keys():
        result = parse_dict[key]
    else:
        result = ""
    return result


def message_parser(text):
    message = parse_1(text)['message']
    time = parse_1(text)['time']

    spaces = pp.White('\t \n\r')
    hours = pp.Word(pp.nums)('hours')
    minutes = pp.Word(pp.nums)('minutes')
    pretime = (pp.Optional(pp.Word(pp.nums))('days') + pp.oneOf(list(shift_selector.keys()))('shift'))('pretime')
    # time0 = (hours + pp.oneOf(list(':.чЧдД')) + minutes + pp.Optional(pp.oneOf(list('мМ'))) |
    #          hours + pp.Optional(pp.oneOf(list(':.чЧдД'))) |
    #          minutes + pp.Optional(pp.oneOf(list('мМ'))))('time')
    time0 = (hours + pp.oneOf(list(':.чЧдД')) + minutes + pp.Optional(pp.oneOf(list('мМ')))|minutes + pp.oneOf(list('мМ'))|hours)('time')
    time_parser = pp.LineStart() + pp.Optional(pretime) + time0 + pp.Optional(spaces) + pp.LineEnd()

    try:
        tim = time_parser.parseString(time)
    except:
        return []
    else:
        out_days = assign(tim, 'days')
        out_shift = assign(tim, 'shift')
        out_hours = assign(tim, 'hours')
        out_minutes = assign(tim, 'minutes')

        print('days = ' + out_days)
        print('shft = ' + out_shift)
        print('hors = ' + out_hours)
        print('mins = ' + out_minutes)

        if out_days: out_days = int(out_days)
        else: out_days = 0
        if out_hours: out_hours = int(out_hours)
        else: out_hours = 0
        if out_minutes: out_minutes = int(out_minutes)
        else: out_minutes = 0

        return [message, out_shift, out_days, out_hours, out_minutes]


# def main():
#     result = message_parser('+3:25')
#     exit(0)
#
# main()
