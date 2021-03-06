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

QUE_NUM, MOD_NM = C.get_name_num(__file__)
RED_CHAN = str( QUE_NUM)
#RED_CHAN = str( QUE_NUM + QUE_NUM )
#RED_CHAN2 = str(QUE_NUM + QUE_NUM + 1 )

from celery import Celery
from celery.schedules import crontab
from .common import settings, db, Field

proj_name = os.path.basename(__file__).replace('.py','')
r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)

app = Celery(
    #f"{C.cel_files_pre}__stuff",
    f"{proj_name}__stuff",
    #broker = 'redis://localhost:6379/0',
    broker= f"redis://localhost/{RED_CHAN}",
#    backend= f"redis://localhost/{RED_CHAN2}",

#    namespace=C.sio_channel,
)
app.control.purge()

TIME_schedule= 5.0
@app.task(ignore_result=True)
def lorem_msg():
    from random import randrange


    ev_name = sys._getframe().f_code.co_name
    some_id = str(randrange(1, 10))
    tbl = "test_table"
    try:
        some_id = int(some_id)
        db._adapter.reconnect()
        r = db(db[tbl].id == some_id).select().first()
        res = [
            f"{k}={v}"
            for k, v in r.items()
            if not k in ("update_record", "delete_record")
        ]
        msg = "{}.select:  {}".format(tbl, " ".join(res))
        r_mgr.emit(ev_name, msg, broadcast=True, include_self=False)
    except Exception as ex:
        # print(sys.exc_info())
        ex_info = str(sys.exc_info()[0]).split(" ")[1].strip(">").strip("'")
        msg = f"!!! error in {ev_name}, id={some_id}, table={tbl}" + ex_info
        r_mgr.emit(ev_name, msg, broadcast=True, include_self=False)


app.conf.beat_schedule = {
    "lorem_msg-task": {
        "task": f"{C.APPS_DIR}.{C.P4W_APP}.{MOD_NM}.lorem_msg",
        "schedule": TIME_schedule,
        "args": (),
        "options": {"queue": f"{C.cel_queue_pre}{QUE_NUM}"},
    },
}
