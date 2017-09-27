from celery import Celery
import vk
import time


token = <token>


app = Celery('tasks', backend='amqp', broker='amqp://')
api = vk.API(vk.Session(access_token=token))


def return_humanity_time():
    return str(time.strftime('%H:%M:%S'))


@app.task
def send_notification(user_ids_list, mess):
    try:
        api.messages.send(user_ids=user_ids_list, message=mess)
        print(return_humanity_time() + ' message sent: ' + mess + ' ids=' + str(user_ids_list))
    except Exception as inst:
        print("can\'t send notification")
