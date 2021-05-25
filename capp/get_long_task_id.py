import sys, os
#sys.path.append(os.path.abspath('/home/w3p/set1/py4web'))
sys.path.append(os.path.abspath('./'))


from apps.capp.celery_stuff import  long_task # Importing the task


def start_serve_a_long_task():
    """ Starts the execution of a celery task with the delay method.
    the delay method doesn't wait the task execution be finished.
    """
    xxx= long_task.apply_async(('weiss', '500ml'))
    print(f'task_id {xxx} will be executed before the serve_a_beer task be finished')
    print ('task_status: ',xxx.status)

start_serve_a_long_task()


