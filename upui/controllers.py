from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from py4web.utils.factories import Inject
from py4web.utils.cors import CORS
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
import os,sys

import socketio
import datetime
import json


from . import chan_conf as C

r_mgr = socketio.RedisManager(C.r_url, write_only=True, channel=C.sio_channel)


@action("sio_pusher", method=["GET", "POST"])
def sio_pusher():
    data_str = 'hello from sio_pusher'
    r_mgr.emit("pydal_msg", data_str, broadcast=True, include_self=False)
    return None

@action("pgs_reload", method=["GET", "POST"])
def pgs_reload():
    data_str = 'from pgs_reload ' + datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    r_mgr.emit("pgs_reload", data_str, broadcast=True, include_self=False)
    return None

load1, load5, load15  = C.inject_load()
sio_serv_url = C.sio_serv_url

@unauthenticated("index", "index.html")

@action.uses(  CORS(),Inject( load1=load1, load5=load5, load15=load15, sio_serv_url=sio_serv_url )  )

def index():
    user = auth.get_user()
    date_str = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    return dict(message=message, date_str=date_str)

#@app.route('/page2')
@action("page2", method=["GET", "POST"])
@action.uses(db, session, T,  CORS(), "index2.html")
@action.uses( Inject( load1=load1, load5=load5, load15=load15, sio_serv_url=sio_serv_url )  )
def page2():
    date_str = datetime.datetime.now().strftime("%d.%m.%y %H:%M:%S")
    return locals()

# --------------------------------------------------------------------------------------
@action("sio_chan_post", method=["POST"])
@action.uses(  CORS() )
def sio_chan_post():

    try:
       json_data = json.loads( request.body.read()   )

       event_name = json_data["event_name"]
       room = json_data["room"]
       data = json_data["data"]
       if json_data["broadcast_secret"] == C.BROADCAST_SECRET:
            cat_value = request.get_header('app-param')
            print ('from sio_chan_post header: ', cat_value  )
            print("json-post-data: ", json_data)
    except Exception as ex:
        print ('sio_chan_post: ',ex )
        print(sys.exc_info())
        return 'bad'

    return "ok"



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
