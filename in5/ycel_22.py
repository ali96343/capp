#
import sys, os
import datetime
import json
import socketio
import requests

this_dir = os.path.dirname( os.path.abspath(__file__) )
if not this_dir in sys.path:
    sys.path.insert(0, this_dir)

#from . import chan_conf as C
import chan_conf as C



QUE_NUM, MOD_NM = C.get_name_num(__file__)
RED_CHAN= str( QUE_NUM)
#RED_CHAN= str( QUE_NUM + QUE_NUM )
#RED_CHAN2 = str( QUE_NUM + QUE_NUM + 1 )

from celery import Celery
from celery.schedules import crontab
from .common import settings, db, Field

proj_name = os.path.basename(__file__).replace('.py','')

r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)

app = Celery(
    #f"{C.cel_files_pre}__stuff",
    f"{proj_name}__stuff",
    broker= f"redis://localhost/{RED_CHAN}",
    #broker = 'redis://localhost:6379/0',
#    backend= f"redis://localhost/{RED_CHAN2}",

#    namespace=C.sio_channel,
)
app.control.purge()

TIME_schedule= 1.0
@app.task(ignore_result=True)
def update_chart():
    data_str = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    r_mgr.emit("update_date", data_str, broadcast=True, include_self=False)
    import random
    chart_data = json.dumps( dict( value=random.randint( 10, 90) )   )
    ev_name = sys._getframe().f_code.co_name
    r_mgr.emit(ev_name, chart_data, broadcast=True, include_self=False)
    C.sync_event_post( "update_date", data=data_str,)


app.conf.beat_schedule = {
    "update_chart-task": {
        "task": f"{C.APPS_DIR}.{C.P4W_APP}.{MOD_NM}.update_chart",
        "schedule": TIME_schedule,
        "args": (),
        "options": {"queue": f"{C.cel_queue_pre}{QUE_NUM}"},
    },
}
