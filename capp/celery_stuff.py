#
import sys, os

sys.path.append(
    os.path.abspath("./")
)  # == sys.path.append(os.path.abspath('/home/w3p/set1/py4web'))


from time import sleep
from celery import Celery
from celery.schedules import crontab
from apps.capp.common import settings, scheduler, db, Field

# Creating a celery instance with redis as message broker.
app = Celery(
    "celery_stuff", broker="redis://localhost/2", backend="redis://localhost/3"
)

app.control.purge()


# celery -A apps.capp.celery_stuff worker -l debug -Q beer,coffee,pydal
# app.conf.task_routes = {
#    'serve_a_beer': {'queue': 'beer'},
#    'serve_a_coffee': {'queue': 'coffee'},
#    'read_db': {'queue': 'pydal'}
# }

# https://overcoder.net/q/935361/%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B8%D1%82%D1%8C-%D1%80%D0%B5%D0%B7%D1%83%D0%BB%D1%8C%D1%82%D0%B0%D1%82-%D0%B8%D0%B7-taskid-%D0%B2-celery-%D0%B8%D0%B7-%D0%BD%D0%B5%D0%B8%D0%B7%D0%B2%D0%B5%D1%81%D1%82%D0%BD%D0%BE%D0%B3%D0%BE-%D0%B7%D0%B0%D0%B4%D0%B0%D0%BD%D0%B8%D1%8F


# https://antoniodimariano.medium.com/how-to-run-periodic-tasks-in-celery-28e1abf8b458
# celery -A apps.capp.celery_stuff beat -l info
# celery -A apps.capp.celery_stuff worker -l info

# https://testdriven.io/blog/django-celery-periodic-tasks/



@app.task
def check():
    print("110 sec! I am checking your stuff")

@app.task
def run_every_min():
    print("everyday-task min")

# https://webdevblog.ru/python-celery/
# https://medium.com/the-andela-way/crontabs-in-celery-d779a8eb4cf
app.conf.beat_schedule = {
    "run-me-every-ten-seconds": {
        "task": "apps.capp.celery_stuff.check",
        "schedule": 110.0,
    },
    "everyday-task": {
        "task": "apps.capp.celery_stuff.run_every_min",
        #"schedule": crontab(hour=22, minute=0),
        'schedule': crontab(minute='*', )
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


@app.task
def serve_a_beer(_type, size):
    """
     This is a celery task. Just a normal function with task decorator.
     Note that we use the decorator from a celery insance.
    """
    print("Serving {} of {} beer!".format(size, _type))
    sleep(3)
    print(
        """
          ------------------------------------------------
                   .   *   ..  . *  *
                 *  * @()Ooc()*   o  .
                     (Q@*0CG*O()  ___
                    |\_________/|/ _ \\
                    |  |  |  |  | / | |
                    |  |  |  |  | | | |
                    |  |  |  |  | | | |
                    |  |  |  |  | | | |
                    |  |  |  |  | | | |
                    |  |  |  |  | \_| |
                    |  |  |  |  |\___/  
                    |\_|__|__|_/|
                     \_________/
          ------------------------------------------------
          """
    )


@app.task
def serve_a_coffee(_type, size):
    """
     This is a celery task. Just a normal function with task decorator.
     Note that we use the decorator from a celery insance.
    """
    print("Serving a {} {} coffee!".format(size, _type))
    sleep(1)
    print(
        """
          ---------------------------------
                          )  (
                         (   ) )
                          ) ( (
                     mrf_______)_
                     .-'---------|  
                    ( C|/\/\/\/\/|
                     '-./\/\/\/\/|
                       '_________'
                        '-------'
          ---------------------------------
          """
    )


@app.task
def read_db(some_id="1", tbl="test_table"):
    print("Serving record id={}, table={}".format(some_id, tbl))
    try:
        some_id = int(some_id)
        # this task will be executed in its own thread, connect to db
        db._adapter.reconnect()
        r = db(db[tbl].id == some_id).select().first()
        print(r)
        res = [
            f"{k}={v}"
            for k, v in r.items()
            if not k in ("update_record", "delete_record")
        ]
        print("result:\n ", ",\n ".join(res))
    except:
        print(f"!!! error in read_db, id={some_id}, table={tbl}")


# https://stackoverflow.com/questions/5544629/retrieve-list-of-tasks-in-a-queue-in-celery
