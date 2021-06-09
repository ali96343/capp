from random import randint
from time import sleep
from celery import Celery

# Start a celery instance
#celery = Celery('tasks', broker="redis://localhost/2", backend="redis://localhost/3" )
celery = Celery('celery_tasks', broker='redis://localhost:6379/0', backend='rpc://')
#celery = Celery('tasks', broker='redis://localhost:6379/0', backend='rpc://')
celery.control.purge()
#celery = Celery('tasks', broker='redis://redis:6379/0', backend='rpc://')


@celery.task
def slow_add(num1, num2):
    """
    Slowly add two numbers, replicating a long-running task.

    :param num1: First digit to add
    :param num2: Second digit to add
    :return: Sum of num1 and num2
    """
    
    # Sleep between 0 and 3 seconds
    sleep(randint(3, 6))

    # Sum and return
    return num1 + num2
    #return a + b
