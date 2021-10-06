#
import sys, os
import datetime
import json
import socketio
import requests

this_dir = os.path.dirname( os.path.abspath(__file__) )
if not this_dir in sys.path:
    sys.path.insert(0, this_dir)

from . import chan_conf as C
QUE_NUM, MOD_NM = C.get_name_num(__file__)
RED_CHAN= str( QUE_NUM + QUE_NUM )
RED_CHAN2 = str( QUE_NUM + QUE_NUM + 1 )

from time import sleep
from celery import Celery
from celery.schedules import crontab
from .common import settings, db, Field

r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)

app = Celery(
    f"{C.cel_files_pre}stuff",
    broker= f"redis://localhost/{RED_CHAN}",
    backend= f"redis://localhost/{RED_CHAN2}",

    namespace=C.sio_channel,
)
app.control.purge()


@app.task
def emit_date():
    data_str = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    r_mgr.emit("update_date", data_str, broadcast=True, include_self=False)
    C.sync_event_post(
        "update_date", data=data_str,
    )


app.conf.beat_schedule = {
    "emit-date-task": {
        "task": f"{C.APPS_DIR}.{C.P4W_APP}.{MOD_NM}.emit_date",
        "schedule": 1.0,
        "args": (),
        "options": {"queue": f"{C.cel_queue_pre}{QUE_NUM}"},
    },
}
