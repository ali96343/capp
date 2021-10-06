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
RED_CHAN = str( QUE_NUM + QUE_NUM )
RED_CHAN2 = str(QUE_NUM + QUE_NUM + 1 )

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
def read_db():
    from random import randrange

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
        r_mgr.emit("lorem_msg", msg, broadcast=True, include_self=False)
    except Exception as ex:
        # print(sys.exc_info())
        ex_info = str(sys.exc_info()[0]).split(" ")[1].strip(">").strip("'")
        msg = f"!!! error in read_db, id={some_id}, table={tbl}" + ex_info
        r_mgr.emit("lorem_msg", msg, broadcast=True, include_self=False)


app.conf.beat_schedule = {
    "read-db-task": {
        "task": f"{C.APPS_DIR}.{C.P4W_APP}.{MOD_NM}.read_db",
        "schedule": 5.0,
        "args": (),
        "options": {"queue": f"{C.cel_queue_pre}{QUE_NUM}"},
    },
}
