from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, I, SPAN, XML, DIV, P

from .common import (
    db,
    session,
    T,
    cache,
    auth,
    logger,
    authenticated,
    unauthenticated,
    flash,
)
from py4web import action, request, response, abort, redirect, URL, Field
from .settings import APP_NAME
import os, sys

DAPPS = "apps" # py4web apps dir

cel_log_worker= f"/tmp/{APP_NAME}.worker.log"
cel_log_beat= f"/tmp/{APP_NAME}.beat.log"

all_cmds = {
    "redis": "ps axw| grep redis-server| grep -v grep",
    "celery": "ps axw| grep celery| grep -v grep",
    "kill_cel": "for pid in $(ps -ef | awk '/celery/ {print $2}'); do kill -9 $pid; done",
    "run_cel_worker": f"celery -A {DAPPS}.{APP_NAME}.celery_stuff worker -l info -f {cel_log_worker} --detach", 
    "run_cel_beat": f"celery -A {DAPPS}.{APP_NAME}.celery_stuff beat -l info -f {cel_log_beat} --detach", 

}


from .celery_stuff import long_task, my_background_task
from .celery_stuff import app as celery_app 

# from apps.capp.celery_stuff import long_task, my_background_task

# jsonify
# https://stackoverflow.com/questions/7907596/json-dumps-vs-flask-jsonify


@unauthenticated("index", "index.html")
def index():
    user = auth.get_user()
    message = T(
        "Hello, {first_name}!".format(**user)
        if user
        else f"Hello, anonymous! its {APP_NAME}"
    )
    if any([APP_NAME != "capp", not os.path.isdir("../py4web/apps/capp")]):
        menu = DIV(P("errors in setup: bad APP_NAME, apps-dir ..."))
        return locals()

    menu = DIV(
        P("py4web+celery+redis;"),
        P(
            "https://medium.com/analytics-vidhya/asynchronous-tasks-in-python-with-celery-e6a9d7e3b33d"
        ),
        P(
            "run from py4web-dir: celery -A apps.capp.celery_stuff worker --loglevel=info "
        ),
        P(
            "run from py4web-dir: celery -A apps.capp.celery_stuff beat --loglevel=info "
        ),
        DIV(
            A("pwd", _role="button", _href=URL("command_server", vars=dict(cmd="pwd"))),
            A("ls .", _role="button", _href=URL("command_server", vars=dict(cmd="ls"))),
            A(
                f"ls {DAPPS}/{APP_NAME}",
                _role="button",
                _href=URL("command_server", vars=dict(cmd=f"ls {DAPPS}/{APP_NAME}")),
            ),
            A(
                "check redis-server",
                _role="button",
                _href=URL("command_server", vars=dict(cmd=all_cmds["redis"])),
            ),
        ),
        DIV(
            A(
                "check celery",
                _role="button",
                _href=URL("command_server", vars=dict(cmd=all_cmds["celery"])),
            ),
            A(
                "run celery worker",
                _role="button",
                _href=URL(
                    "command_server", vars=dict( cmd = all_cmds[ "run_cel_worker"  ] )), 
            ),
            A(
                "run celery beat",
                _role="button",
                _href=URL(
                    "command_server", vars=dict( cmd = all_cmds[ "run_cel_beat"  ] )), 
            ),
            A(
                "kill celery",
                _role="button",
                _href=URL("command_server", vars=dict(cmd=all_cmds["kill_cel"])),
            ),
        ),
        DIV(
            A(
                "cat celery_stuff.py",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"cat {DAPPS}/{APP_NAME}/celery_stuff.py"),
                ),
            ),
            A(
                "cat first_app.py",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"cat {DAPPS}/{APP_NAME}/first_app.py"),
                ),
            ),
        ),
        DIV(
            A(
                "run first_app.py",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"python3 {DAPPS}/{APP_NAME}/first_app.py"),
                ),
            ),
            A(
                "celery queue",
                _role="button",
                _href=URL( "celery_queue_status",),
            ),

        ),
        DIV(A("run longtask", _role="button", _href=URL("longtask"))),
        DIV(
            A(
                "get beer id",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"python3  {DAPPS}/{APP_NAME}/get_beer.py"),
                ),
            ),
            A(
                "get beer_res; wait result, pls",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"python3  {DAPPS}/{APP_NAME}/get_beer_res.py"),
                ),
            ),
        ),
        DIV(
            A(
                "get coffee id",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"python3  {DAPPS}/{APP_NAME}/get_coffee.py"),
                ),
            ),
            A(
                "get coffee_res; wait result, pls",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"python3  {DAPPS}/{APP_NAME}/get_coffee_res.py"),
                ),
            ),
        ),
        DIV(
            A(
                "get read_db id",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"python3  {DAPPS}/{APP_NAME}/get_db_row.py"),
                ),
            ),
            A(
                "get read_db_res; wait result, pls",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"python3  {DAPPS}/{APP_NAME}/get_db_row_res.py"),
                ),
            ),
        ),
        _style="font-size:18px;",
    )

    return locals()


import subprocess


def run_command(command="ls"):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()


@action("command_server", method=["POST", "GET"])
def command_server():

    cmd_d = dict(request.query)
    cmd = cmd_d.get("cmd", "ls")
    res = b"<pre>" + run_command(cmd).replace(b"\n", b"<br>") + b"</pre>"
    b_cmd = b"$ " + cmd.encode()  # b'some-mess'

    return DIV(b_cmd + b"<br>" + res, _style="font-size:18px;")


# https://blog.miguelgrinberg.com/post/using-celery-with-flask
@action("longtask", method=["POST", "GET"])
def longtask():
    task = long_task.apply_async()
    print(task)
    print(task.id)
    print(task.status)
    if task and task.status == "PENDING":
        task_id = task.id
        redirect(URL("taskstatus/task_id"))
    celery_queue_status()
    return f"{task}"
    # return jsonify({}), 202, {'Location': url_for('taskstatus',
    #                                              task_id=task.id)}


@action("taskstatus/<task_id:path>")
def taskstatus(task_id=None):
    import json

    task = long_task.AsyncResult(task_id)
    res = {}
    if task.state == "PENDING":
        # job did not start yet
        res = {
            "state": task.state,
            "current": 0,
            "total": 1,
            "status": "Pending...",
        }
    elif task.state != "FAILURE":
        res = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": task.info.get("total", 1),
            "status": task.info.get("status", ""),
        }
        if "result" in task.info:
            res["result"] = task.info["result"]
    else:
        # something went wrong in the background job
        res = {
            "state": task.state,
            "current": 1,
            "total": 1,
            "status": str(task.info),  # this is the exception raised
        }
    return json.dumps(res)
    # return jsonify(response)

@action("celery_queue_status")
def celery_queue_status():

   print ("!!! from celery_queue_status: ")
   # Inspect all nodes.
   i = celery_app.control.inspect()
   print ("Inspect all nodes: ", i)

   # Show the items that have an ETA or are scheduled for later processing
   print ("Show the items that have an ETA or are scheduled for later processing: ",i.scheduled() )

   # Show tasks that are currently active.
   print ("Show tasks that are currently active: ", i.active() )

   # Show tasks that have been claimed by workers
   print ("Show tasks that have been claimed by workers: ", i.reserved() )
   
   return 'ok, result in py4web-shell'
