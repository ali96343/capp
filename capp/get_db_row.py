import sys, os
#sys.path.append(os.path.abspath('/home/w3p/set1/py4web'))
sys.path.append(os.path.abspath('./'))


from apps.capp.celery_stuff import  read_db # Importing the task

def start_read_db():
    """ Starts the execution of a celery task with the delay method.
    the delay method doesn't wait the task execution be finished.
    """
    xxx=read_db.apply_async( ( '1', 'test_table' ) )
    print( f'task_id {xxx} will be executed before the read_db task be finished')


start_read_db()


