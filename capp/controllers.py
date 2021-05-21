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

all_cmd = {
    "redis": "ps axw| grep redis-server| grep -v grep",
    "celery": "ps axw| grep celery| grep -v grep",
    "kill_cel":"for pid in $(ps -ef | awk '/celery/ {print $2}'); do kill -9 $pid; done",
}


@unauthenticated("index", "index.html")
def index():
    user = auth.get_user()
    message = T(
        "Hello, {first_name}!".format(**user)
        if user
        else f"Hello, anonymous! its {APP_NAME}"
    )
    APPS = "apps"
    if not os.path.isdir('../py4web/apps/capp'):
        menu = DIV(P("errors in setup: bad APP_NAME, apps-dir ..."))
        return locals()

    menu = DIV(
        P("py4web+celery+redis;" ),
        P("https://medium.com/analytics-vidhya/asynchronous-tasks-in-python-with-celery-e6a9d7e3b33d"),
        P("run from py4web-dir: celery -A apps.capp.celery_stuff worker --loglevel=info " ),

        A("pwd", _role="button", _href=URL("command_server", vars=dict(cmd="pwd"))),
        A("ls .", _role="button", _href=URL("command_server", vars=dict(cmd="ls"))),
        A(
            f"ls {APPS}/{APP_NAME}",
            _role="button",
            _href=URL("command_server", vars=dict(cmd=f"ls {APPS}/{APP_NAME}")),
        ),
        DIV(
            A(
                "check redis",
                _role="button",
                _href=URL("command_server", vars=dict(cmd=all_cmd["redis"])),
            )
        ),
        DIV(
            A(
                "check celery",
                _role="button",
                _href=URL("command_server", vars=dict(cmd=all_cmd["celery"])),
            ),
            A(
                "run celery",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(
                        cmd=f"celery -A {APPS}.{APP_NAME}.celery_stuff worker --loglevel=info --detach"
                    ),
                ),
            ),
            A(
                "kill celery",
                _role="button",
                _href=URL("command_server", vars=dict(cmd=all_cmd["kill_cel"])),
            ),
        ),
        DIV(
            A(
                "cat celery_stuff.py",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"cat {APPS}/{APP_NAME}/celery_stuff.py"),
                ),
            ),
            A(
                "cat first_app.py",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"cat {APPS}/{APP_NAME}/first_app.py"),
                ),
            ),
        ),
        DIV(
            A(
                "run first_app.py",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"python3 {APPS}/{APP_NAME}/first_app.py"),
                ),
            )
        ),
        DIV(
            A(
                "get beer id",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd=f"python3  {APPS}/{APP_NAME}/get_beer.py")
                ),
            ),
            A(
                "get beer_res",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd=f"python3  {APPS}/{APP_NAME}/get_beer_res.py")
                ),
            )
        ),
        DIV(
            A(
                "get coffee id",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd=f"python3  {APPS}/{APP_NAME}/get_coffee.py")
                ),
            ),
            A(
                "get coffee_res",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd=f"python3  {APPS}/{APP_NAME}/get_coffee_res.py")
                ),
            )
        ),
        DIV(
            A(
                "get read_db id",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd=f"python3  {APPS}/{APP_NAME}/get_db_row.py")
                ),
            ),
            A(
                "get read_db_res",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd=f"python3  {APPS}/{APP_NAME}/get_db_row_res.py")
                ),
            )
        ),
    _style= "font-size:18px;")

    return locals()


import subprocess


def run_command(command="ls"):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()


@action("command_server", method=["POST", "GET"])
def command_server():

    cmd_d = dict(request.query)
    cmd = cmd_d.get("cmd", "ls")
    res = b'<pre>' + run_command(cmd).replace(b"\n", b"<br>") + b'</pre>'
    b_cmd = b"$ " + cmd.encode()  # b'some-mess'

    return DIV( b_cmd + b"<br>" + res, _style= "font-size:18px;" )
