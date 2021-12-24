#
import sys, os
import datetime
import json
import socketio
import requests

this_dir = os.path.dirname(os.path.abspath(__file__))
if not this_dir in sys.path:
    sys.path.insert(0, this_dir)

import chan_conf as C

# from . import chan_conf as C

QUE_NUM, MOD_NM = C.get_name_num(__file__)
RED_CHAN = str(QUE_NUM)
# RED_CHAN = str(QUE_NUM + QUE_NUM )
# RED_CHAN2 = str(QUE_NUM + QUE_NUM + 1 )


# -----------------------------------------------------------------
# https://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html#id1


import time

# from celery import task
from celery.utils.log import get_task_logger
from contextlib import contextmanager
from celery.exceptions import SoftTimeLimitExceeded


# from django.core.cache import cache
from hashlib import md5

# import memcache
from pymemcache.client import base   # pip install pymemcache

# from djangofeeds.models import Feed

logger = get_task_logger(__name__)

# LOCK_EXPIRE = 20  # Lock expires in 10 minutes
LOCK_EXPIRE = 60 * 10  # Lock expires in 10 minutes


# cache = memcache.Memcache() #['127.0.0.1:11211'], debug=0)
cache = base.Client(("localhost", 11211))


@contextmanager
def memcache_lock(lock_id, oid):
    timeout_at = time.monotonic() + LOCK_EXPIRE - 3
    # cache.add fails if the key already exists
    status = cache.add(lock_id, oid, LOCK_EXPIRE)
    try:
        yield status
    finally:
        # memcache delete is very slow, but we have to use it to take
        # advantage of using add() for atomic locking
        if time.monotonic() < timeout_at and status:
            # don't release the lock if we exceeded the timeout
            # to lessen the chance of releasing an expired lock
            # owned by someone else
            # also don't release the lock if we didn't acquire it
            cache.delete(lock_id)


# -----------------------------------------------------------------


from celery import Celery
from celery.schedules import crontab
from .common import settings, db, Field

proj_name = os.path.basename(__file__).replace(".py", "")
r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)

app = Celery(
    f"{proj_name}__stuff",
    # f"{C.cel_files_pre}__stuff",
    # broker = 'redis://localhost:6379/0',
    broker=f"redis://localhost/{RED_CHAN}",
    #    backend= f"redis://localhost/{RED_CHAN2}",
    #namespace=C.sio_channel,
)
app.control.purge()


# super !!!
# https://testdriven.io/blog/retrying-failed-celery-tasks/


TIME_schedule= 10.0
@app.task(ignore_result=True, soft_time_limit=3, time_limit=5  )
def update_joke():

    # @celery.task( retry_backoff=5, max_retries=7, retry_jitter=False,)
    # https://breadcrumbscollector.tech/what-is-celery-beat-and-how-to-use-it-part-2-patterns-and-caveats/
    # http://loose-bits.com/2010/10/distributed-task-locking-in-celery.html
    # https://stackoverflow.com/questions/20975428/how-to-implement-a-lockfile-like-mechanism-between-celery-workers

    joke_url = "http://api.icndb.com/jokes/random"
    msg, joke, ex_info  = None, None, None

    ev_name = sys._getframe().f_code.co_name
    try:
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':RC4-SHA'
        res = requests.get(joke_url,timeout=3 )

        if res.status_code == 200:
            res_json = res.json()
            joke = res_json["value"]["joke"]
        else:
            joke = f"!!! error in {ev_name}, url={joke_url}"


    except SoftTimeLimitExceeded:
        joke = "Oups, soft limit exceeded! Quickly, clean up!"

    except Exception as ex:
        ex_info = str(sys.exc_info()[0]).split(" ")[1].strip(">").strip("'")
        joke = f"!!! error in {ev_name}, url={joke_url}" + ex_info

    msg = json.dumps(dict(joke=joke,))
    r_mgr.emit(ev_name, msg, broadcast=True, include_self=False)


app.conf.beat_schedule = {
    "update_joke-task": {
        "task": f"{C.APPS_DIR}.{C.P4W_APP}.{MOD_NM}.update_joke",
        "schedule": TIME_schedule,
        "args": (),
        "options": {"queue": f"{C.cel_queue_pre}{QUE_NUM}"},
    },
}
