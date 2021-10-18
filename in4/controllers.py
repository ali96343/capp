from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from py4web.utils.factories import Inject
from py4web.utils.cors import CORS
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
from .settings import APP_NAME
import ombott  # as ombott

import os, sys

import socketio
import datetime
import json


from . import chan_conf as C

r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)

from random import randrange


load1, load5, load15 = C.inject_load()

html_vars = {
    "load1": load1,
    "load5": load5,
    "load15": load15,
    "sio_serv_url": C.sio_serv_url,
    "sio_app": C.P4W_APP,
    "sio_port": C.sio_PORT,
    "jpeg_stream_url": C.jpeg_stream_url,
    "video_stream_url": C.video_stream_url,
    "index": f"/{APP_NAME}/index",
    "page2": f"/{APP_NAME}/page2",
    "ssepage": f"/{APP_NAME}/ssepage",
    "chart": f"/{APP_NAME}/chart",
    "sse_url": C.sse_url,
}


def get_row(tbl="test_table"):
    some_id = str(randrange(1, 10))
    r = db[tbl](some_id)
    res = [
        f"{k}={v}" for k, v in r.items() if not k in ("update_record", "delete_record")
    ]
    return "{}.select:  {}".format(tbl, " ".join(res))


@action("sio_pusher", method=["GET", "POST"])
def sio_pusher():
    data_str = "! sio_pusher " + datetime.datetime.now().strftime("%H:%M:%S")
    r_mgr.emit("pydal_msg", data_str, broadcast=True, include_self=False)
    return None


@action("pgs_reload", method=["GET", "POST"])
def pgs_reload():
    data_str = "! pgs_reload " + datetime.datetime.now().strftime("%H:%M:%S")
    r_mgr.emit("pgs_reload", data_str, broadcast=True, include_self=False)
    return None


@unauthenticated("index", "index.html")
def index():
    user = auth.get_user()
    date_str = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    lorem1 = get_row()

    t_vars = html_vars
    return locals()


@action("page2", method=["GET", "POST"])
@action.uses(db, session, T, CORS(), "index2.html")
def page2():
    date_str = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    lorem2 = get_row()

    t_vars = html_vars
    return locals()


@action("ssepage", method=["GET", "POST"])
@action.uses(db, session, T, CORS(), "sse-page.html")
def ssepage():
    date_str = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    sselorem = get_row()

    t_vars = html_vars
    return locals()


@action("chart", method=["GET", "POST"])
@action.uses(db, session, T, CORS(), "chart.html")
def chart():

    t_vars = html_vars
    return locals()


@action("lorem_get", method=["GET"])
@action.uses(CORS())
def lorem_get():
    sselorem = get_row()

    # t_vars = html_vars
    return sselorem


# --------------------------------------------------------------------------------------
@action("sio_chan_post", method=["POST"])
@action.uses(CORS())
def sio_chan_post():

    try:
        json_data = json.loads(request.body.read())

        event_name = json_data["event_name"]
        room = json_data["room"]
        data = json_data["data"]
        if json_data["broadcast_secret"] == C.BROADCAST_SECRET:
            cat_value = ""  # request.get_header('app-param')
            cat_value = request.headers.get("app-param", "xxxxxxxx")
            C.sio_debug and print("from sio_chan_post header: ", cat_value)
            C.sio_debug and print("json-post-data: ", json_data)
    except Exception as ex:
        print("sio_chan_post: ", ex)
        print(sys.exc_info())
        return "bad"

    return "ok"


# https://stribny.name/blog/2020/07/real-time-data-streaming-using-fastapi-and-websockets/
# https://github.com/stribny/python-web-realtime-streaming

# @ombott.error(404, '/web<_:path()>')
# @ombott.error(404, '/web/<params:path>')
@ombott.error(404, f"/{APP_NAME}")
def url_not_found(route, params):
    # print ( str(dict(route=route, params=params))  )

    ombott.response.status = 303
    ombott.response.headers["Location"] = f"/{APP_NAME}"
    #ombott.response.headers['Location'] = route #f'/{APP_NAME}'




#
#    def read_body(request):
#        if "wsgi.input" in request:
#            post_data = request["wsgi.input"].read()
#            if isinstance(post_data, bytes):
#                return json.loads(post_data)
#        return None
#
#    json_data = read_body(request)
#
#    if json_data:
#        event_name = json_data["event_name"]
#        room = json_data["room"]
#        data = json_data["data"]
#        if json_data["broadcast_secret"] == C.BROADCAST_SECRET:
#            print("json-post-data: ", json_data)
#
#    return "ok"
#
