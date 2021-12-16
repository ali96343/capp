from celery import Celery


from celery.events import EventReceiver

def my_monitor:
    connection = BrokerConnection('amqp://guest:guest@localhost:5672//')

    def on_event(event):
        print "EVENT HAPPENED: ", event

    def on_task_failed(event):
        exception = event['exception']
        print "TASK FAILED!", event, " EXCEPTION: ", exception

    while True:
        try:
            with connection as conn:
                recv = EventReceiver(conn,
                                 handlers={'task-failed' : on_task_failed,
                                           'task-succeeded' : on_event,
                                           'task-sent' : on_event,
                                           'task-received' : on_event,
                                           'task-revoked' : on_event,
                                           'task-started' : on_event,
                                           # OR: '*' : on_event
                                           })
            recv.capture(limit=None, timeout=None)
    except (KeyboardInterrupt, SystemExit):
        print "EXCEPTION KEYBOARD INTERRUPT"
        sys.exit()

def my_monitor(app):
    state = app.events.State()

    def announce_failed_tasks(event):
        state.event(event)
        task_id = event['uuid']

        print('TASK FAILED: %s[%s] %s' % (
            event['name'], task_id, state[task_id].info(), ))
    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
                'task-failed': announce_failed_tasks,
                'worker-heartbeat': announce_dead_workers,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)

if __name__ == '__main__':
    celery = Celery(broker='redis://localhost/0')
    #celery = Celery(broker='amqp://guest@localhost//')
    my_monitor(celery)

