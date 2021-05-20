import sys, os
sys.path.append(os.path.abspath('./')) # == sys.path.append(os.path.abspath('/home/w3p/set1/py4web'))


from time import sleep
from celery import Celery

# Creating a celery instance with redis as message broker.

from apps.capp.common import settings, scheduler, db, Field

app = Celery('first_app', broker='redis://localhost/2', backend= 'redis://localhost/3')

app.control.purge()


# celery -A celery_stuff.tasks worker -l debug -Q beer,coffee, pydal
# app.conf.task_routes = {
#    'celery_stuff.serve_a_beer': {'queue': 'beer'},
#    'celery_stuff.serve_a_coffee': {'queue': 'coffee'}
#    'celery_stuff.read_db': {'queue': 'pydal'}
#}

@app.task
def serve_a_beer(_type, size):
    """
     This is a celery task. Just a normal function with task decorator.
     Note that we use the decorator from a celery insance.
    """
    print('Serving {} of {} beer!'.format(size, _type))
    sleep(3)
    print("""
          ------------------------------------------------
                   .   *   ..  . *  *
                 *  * @()Ooc()*   o  .
                     (Q@*0CG*O()  ___
                    |\_________/|/ _ \
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
          """)

@app.task
def serve_a_coffee(_type, size):
    """
     This is a celery task. Just a normal function with task decorator.
     Note that we use the decorator from a celery insance.
    """
    print('Serving a {} {} coffee!'.format(size, _type))
    sleep(1)
    print("""
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
          """)


@app.task
def read_db(_type, size):
    some_id = 1
    print('Serving a {} {} !'.format(size, _type))
    try:
        # this task will be executed in its own thread, connect to db
        db._adapter.reconnect()
        # do something here
        print ('================================')
        qu= db.test_table.id == some_id
        rows = db(qu).select()
        for r in rows:
            print (r)
    except:
        print ('------------------------error in read_db')



