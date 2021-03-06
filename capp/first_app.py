import sys, os
#sys.path.append(os.path.abspath('/home/w3p/set1/py4web'))
sys.path.append(os.path.abspath('./'))


from apps.capp.celery_stuff import serve_a_beer, serve_a_coffee, read_db # Importing the task


def start_serve_a_beer():
    """ Starts the execution of a celery task with the delay method.
    the delay method doesn't wait the task execution be finished.
    """
    serve_a_beer.apply_async(('weiss', '500ml'))
    print('This will be executed before the serve_a_beer task be finished')


def start_serve_a_coffee():
    """ Starts the execution of a celery task with the delay method.
    the delay method doesn't wait the task execution be finished.
    """
    serve_a_coffee.apply_async(('express', 'small'))
    print('This will be executed before the serve_a_beer task be finished')


def start_serve_a_db():
    """ Starts the execution of a celery task with the delay method.
    the delay method doesn't wait the task execution be finished.
    """
    read_db.apply_async(('1', 'test_table'))
    print('This will be executed before the serve_a_beer task be finished')



start_serve_a_beer()
start_serve_a_coffee()
start_serve_a_db()

