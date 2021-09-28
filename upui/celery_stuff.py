#
import sys, os
import datetime
import json
import socketio
import requests

if not os.path.abspath("./") in sys.path: 
    sys.path.append( os.path.abspath("./"))  

from . import chan_conf as C


from time import sleep
from celery import Celery
from celery.schedules import crontab
from .common import settings, db, Field


r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)

app = Celery( "celery_stuff", broker="redis://localhost/2", backend="redis://localhost/3")
app.control.purge()


def sync_event_post(event_name, data=None, room=None, post=True):


    json_data = {
          "event_name": event_name,
          "data": data,
          "room": room,
          "broadcast_secret": C.BROADCAST_SECRET,
    } 

    headers_dict = {'Content-type': 'application/json', 'Accept': 'text/plain', 
                    "app-param": 'some-param' }
    x = requests.post(C.post_url, json=json_data, headers=headers_dict)

    if x.status_code != 200:
        print(f"error! can not post to: {C.post_url}")



@app.task
def update_loadavg():
    load1, load5, load15 = C.inject_load()  
    l_data = json.dumps( dict( load1=load1, load5=load5, load15=load15  ) )
    # print (l_data)
    r_mgr.emit("update_update", l_data, broadcast=True, include_self=False)
    #print("updated loadavg!")

@app.task
def emit_date():
    data_str = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    r_mgr.emit("update_date", data_str, broadcast=True, include_self=False)
    sync_event_post(  "update_update" , data=data_str, )
    #print("date updated!")

# https://webdevblog.ru/python-celery/
# https://medium.com/the-andela-way/crontabs-in-celery-d779a8eb4cf
app.conf.beat_schedule = {
    "run-me-every-ten-seconds": {
        "task": "apps.%s.celery_stuff.update_loadavg" % settings.APP_NAME  ,
        "schedule": 3.0,
    },
    "everyday-task": {
       "task": "apps.%s.celery_stuff.emit_date" % settings.APP_NAME ,
        "schedule": 1.0,
    },
}


@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def my_background_task(arg1, arg2):
    # some long running task here
    result = "result!!!!"
    return result


@app.task(bind=True)
def long_task(self):
    import random

    """ https://blog.miguelgrinberg.com/post/using-celery-with-flask """

    """Background task that runs a long function with progress reports."""
    verb = ["Starting up", "Booting", "Repairing", "Loading", "Checking"]
    adjective = ["master", "radiant", "silent", "harmonic", "fast"]
    noun = ["solar array", "particle reshaper", "cosmic ray", "orbiter", "bit"]
    message = ""
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = "{0} {1} {2}...".format(
                random.choice(verb), random.choice(adjective), random.choice(noun)
            )
        self.update_state(
            state="PROGRESS", meta={"current": i, "total": total, "status": message}
        )
        sleep(3)
    return {"current": 100, "total": 100, "status": "Task completed!", "result": 42}

