#!/usr/bin/env python

import celery

from datetime import datetime, timedelta

localhost = <localhost>

app = celery.Celery('tasks', backend='amqp', broker='amqp://')


def main():

    print(str(datetime.utcnow()) + ' (CURRENT UTC TIME)\n')

    i = app.control.inspect()
    list1 = i.scheduled()["celery@" + localhost]
    for i in list1:
        timecode = i['eta'].replace('T', ' ')
        print(timecode + '  ' + i['request']['args'])

    return 0


main()
