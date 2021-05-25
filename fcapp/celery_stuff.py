import sys, os
sys.path.append( os.path.abspath("./"))

from time import sleep
from celery import Celery
from apps.fcapp.common import settings, db, Field

# Creating a celery instance with redis as message broker.
app = Celery(
    "celery_stuff", broker="redis://localhost/2", backend="redis://localhost/3"
)

app.control.purge()

@app.task
def my_background_task(arg1, arg2):
    # some long running task here
    result = "result!!!!"
    return result


@app.task
def send_async_email(email_data):
    print (email_data)
    """Background task to send an email with Mail."""
    myrange = 10
    for e in range(myrange):
       print (f'send mail {e}/{myrange}')
       sleep(1)
    return f'ok! from send_async_email: {myrange}'

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

