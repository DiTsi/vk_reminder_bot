#!/bin/bash

sudo rabbitmq-server &

celery -A tasks worker & 

source venv/bin/python
python ./bot.py &

exit 0
