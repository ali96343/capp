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
    "c1": "ps axw| grep redis| grep -v grep",
    "c2": "ps axw| grep celery| grep -v grep",
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
    cwd = os.getcwd()
    p4w = cwd.split("/")[-1]
    if any ( [p4w != "py4web", APP_NAME != 'capp', not os.path.isdir('apps/capp')  ]):
        menu = DIV(P("errors in setup"))
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
                _href=URL("command_server", vars=dict(cmd=all_cmd["c1"])),
            )
        ),
        DIV(
            A(
                "check celery",
                _role="button",
                _href=URL("command_server", vars=dict(cmd=all_cmd["c2"])),
            ),
            A(
                "run celery queue",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(
                        cmd="celery -A apps.capp.celery_stuff worker --loglevel=info --detach"
                    ),
                ),
            ),
        ),
        DIV(
            A(
                "cat celery_stuff.py",
                _role="button",
                _href=URL(
                    "command_server",
                    vars=dict(cmd=f"cat apps/{APP_NAME}/celery_stuff.py"),
                ),
            )
        ),
        DIV(
            A(
                "get beer id",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd="python3  apps/capp/get_beer.py")
                ),
            ),
            A(
                "get beer_res",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd="python3  apps/capp/get_beer_res.py")
                ),
            )
        ),
        DIV(
            A(
                "get coffee id",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd="python3  apps/capp/get_coffee.py")
                ),
            ),
            A(
                "get coffee_res",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd="python3  apps/capp/get_coffee_res.py")
                ),
            )
        ),
        DIV(
            A(
                "get read_db id",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd="python3  apps/capp/get_db_row.py")
                ),
            ),
            A(
                "get read_db_res",
                _role="button",
                _href=URL(
                    "command_server", vars=dict(cmd="python3  apps/capp/get_db_row_res.py")
                ),
            )
        ),
    )

    return locals()


import subprocess


def run_command(command="ls"):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()


@action("command_server", method=["POST", "GET"])
def command_server():

    cmd_d = dict(request.query)
    cmd = cmd_d.get("cmd", "ls")
    res = run_command(cmd).replace(b"\n", b"<br>")
    b_cmd = b"$ " + cmd.encode()  # b'some-mess'

    return b_cmd + b"<br>" + res
