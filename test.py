#!venv/bin/python

import datetime


datet = datetime.datetime.utcnow()
print(str(datet))

datet += datetime.timedelta(hours=1, minutes=15)
print(str(datet))

exit(0)