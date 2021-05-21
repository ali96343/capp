# 
import sys, os
sys.path.append(os.path.abspath('./')) # == sys.path.append(os.path.abspath('/home/w3p/set1/py4web'))


from time import sleep
from celery import Celery

# Creating a celery instance with redis as message broker.

from apps.capp.common import settings, scheduler, db, Field

app = Celery('first_app', broker='redis://localhost/2', backend= 'redis://localhost/3')

app.control.purge()


# celery -A apps.capp.celery_stuff worker -l debug -Q beer,coffee, pydal
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
def read_db(some_id='1', tbl='test_table'):
    some_id = int(some_id)
    print('Serving a id={}, table={} !'.format(some_id, tbl))
    try:
        # this task will be executed in its own thread, connect to db
        db._adapter.reconnect()
        r =  db( db[tbl].id == some_id ).select().first()
        print (r)
        res= [ f"{k}={v}" for k, v in r.items()  if not k in ( 'update_record', 'delete_record' ) ]
        print ( ', '.join(res))
    except:
        print (f'!!! error in read_db, id={some_id}, table={tbl}')

