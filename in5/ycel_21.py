#
import sys, os
import datetime
import json
import socketio
import requests

this_dir = os.path.dirname( os.path.abspath(__file__) )
if not this_dir in sys.path:
    sys.path.insert(0, this_dir)

import chan_conf as C
#from . import chan_conf as C

QUE_NUM, MOD_NM = C.get_name_num(__file__)
RED_CHAN = str(QUE_NUM )
#RED_CHAN = str(QUE_NUM + QUE_NUM )
#RED_CHAN2 = str(QUE_NUM + QUE_NUM + 1 )

from celery import Celery
from celery.schedules import crontab
from .common import settings, db, Field

r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)

proj_name = os.path.basename(__file__).replace('.py','')

app = Celery(
    #f"{C.cel_files_pre}__stuff",
    f"{proj_name}__stuff",
    broker= f"redis://localhost/{RED_CHAN}",
#    backend= f"redis://localhost/{RED_CHAN2}",
#    namespace=C.sio_channel,
)

app.conf.task_send_sent_event=True

app.control.purge()

TIME_schedule= 3.0
@app.task(ignore_result=True)
def update_uptime():
    load1, load5, load15 = C.inject_load()
    l_data = json.dumps(dict(load1=load1, load5=load5, load15=load15))
    ev_name = sys._getframe().f_code.co_name
    r_mgr.emit(ev_name, l_data, broadcast=True, include_self=False)





app.conf.beat_schedule = {
    "update_uptime-task": {
        "task": f"{C.APPS_DIR}.{C.P4W_APP}.{MOD_NM}.update_uptime",
        "schedule": TIME_schedule,
        "args": (),
        "options": {"queue": f"{C.cel_queue_pre}{QUE_NUM}"},
    },
}
