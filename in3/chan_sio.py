#!/usr/bin/env python3

import sys, os

import uvicorn
import socketio
import httpx
import requests

#this_dir = os.path.dirname( __file__ )
this_dir = os.path.dirname( os.path.abspath(__file__) )
if not this_dir in sys.path:
    sys.path.insert(0,  this_dir )
import chan_conf as C

# pip install aioredis==1.3.1

# -----------------------------------------------------------------

# https://github.com/sysid/sse-starlette/blob/master/example.py !!!!!!!!!!!!!!!!

import logging
import asyncio
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.exceptions import HTTPException

from sse_starlette.sse import EventSourceResponse, unpatch_uvicorn_signal_handler

# --------------------------
from starlette.middleware import Middleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware

# Ensure that all requests include an 'example.com' or '*.example.com' host header,
# and strictly enforce https-only access.

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=["GET", "OPTIONS"],
               allow_headers=["Token", "Origin", "X-Requested-With", "Content-Type", "Accept"])
]


# --------------------------

# unpatch_uvicorn_signal_handler()  # if you want to rollback monkeypatching of uvcorn signal-handler

_log = logging.getLogger(__name__)
log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
datefmt = "%m-%d-%Y %H:%M:%S"

if C.sio_debug:
     logging.basicConfig(format=log_fmt, level=logging.DEBUG, datefmt=datefmt)
else:
     logging.basicConfig(format=log_fmt, level=logging.CRITICAL, datefmt=datefmt)

html_sse = """
    <html>
    <body>
<p>You can visit <a href="http://%s:%s/%s/index">Home</a>.</p>
<p>You can visit <a href="http://%s:%s/%s/page2">Page 2</a>.</p>
        <h3>sse numbers < 20 - 1 sec</h3>
        <div id="response"></div>

        <script>
            const evtSource = new EventSource("/numbers");
            const resp=  document.getElementById('response')
            console.log("evtSource: ", evtSource);
            evtSource.onmessage = function(e) {
                if (resp) {
                       resp.innerText = e.data;
                }
                console.log(e);
                if (e.data == 20) {
                    msg = "Closing connection after 20 numbers."
                    console.log(  msg)
                    if (resp) {
                         resp.innerText =  msg ;
                    }
                    evtSource.close()
                }
            }
        </script>
    </body>
</html>
""" % ( C.p4w_host, C.p4w_port, C.P4W_APP,  C.p4w_host, C.p4w_port , C.P4W_APP)


# @sse_app.route('/hello')
async def homepage(request):
    return JSONResponse(content={"message": "hi"})


# @sse_app.route('/hello-test')
async def test(request):
    return JSONResponse(content={"test": "the test route"})


async def numbers(minimum, maximum):
    """Simulates and limited stream"""

    for i in range(minimum, maximum + 1):
        await asyncio.sleep(1.9)
        yield dict(data=i)


async def endless(req: Request):
    """Simulates and endless stream

    In case of server shutdown the running task has to be stopped via signal handler in order
    to enable proper server shutdown. Otherwise there will be dangling tasks preventing proper shutdown.
    """

    async def event_publisher():
        i = 0
        try:
            while True:
                disconnected = await req.is_disconnected()
                if disconnected:
                    _log.info(f"Disconnecting client {req.client}")
                    break
                # yield dict(id=..., event=..., data=...)
                i += 1
                try:
                    async with httpx.AsyncClient() as client:
                        r = await client.get(C.sse_get_data, )
                    yield dict(data=r.text)
                except Exception as ex:
                    _log.info(f"Disconnected from client (via refresh/close) {req.client}")
                    yield dict(data= 'error in endless')
                #yield dict(data=i)
                await asyncio.sleep(1.9)
            _log.info(f"Disconnected from client {req.client}")
        except asyncio.CancelledError as e:
            _log.info(f"Disconnected from client (via refresh/close) {req.client}")
            # Do any other cleanup, if any
            raise e

    return EventSourceResponse(event_publisher())


async def sse(request):
    generator = numbers(1, 25)
    return EventSourceResponse(generator)


async def home(req: Request):
    return HTMLResponse(html_sse)


routes = [
    Route("/", endpoint=home),
    Route("/numbers", endpoint=sse),
    #Route("/endless", endpoint=endless),
    Route("/pydalsse", endpoint=endless),
]

sse_app = Starlette(debug=True, routes=routes, middleware=middleware )


# --------------- global ------------------------------------------

sio_debug = False

#sio_debug and print(f"===: {C.SERV_APP_FILE}")

# ----------------------------------------------------------------
import logging
default_logger = logging.getLogger('tunnel.logger')
default_logger.setLevel(logging.CRITICAL)
default_logger.disabled = True

#self.socket = Server(logger=default_logger,
#                    engineio_logger=default_logger)
# logging.getLogger('socketio').setLevel(logging.ERROR)
# logging.getLogger('engineio').setLevel(logging.ERROR)

r_mgr = socketio.AsyncRedisManager(C.r_url, channel=C.sio_channel,  write_only=False)
sio = socketio.AsyncServer(
    async_mode="asgi",
    client_manager=r_mgr,
    cors_allowed_origins="*",
    SameSite=None,
    logger=default_logger , #sio_debug,
    engineio_logger=default_logger, #sio_debug,
)
app = socketio.ASGIApp(sio, sse_app)
#app = socketio.ASGIApp(sio, static_files={"/": "./public/index.html"})

# --------------------------- utils ----------------------------------------------

async def sio_event_post(event_name, data=None, room=None, post=True):

    # https://zetcode.com/python/httpx/

    json_data = {
        "event_name": event_name,
        "data": data,
        "room": C.sio_room, #room,
        "broadcast_secret": C.BROADCAST_SECRET,
    }

    headers = {'X-Custom': 'value'}

    headers = {
            'app-param': C.P4W_APP, 
            'content-type': "application/json",
            'cache-control': "no-cache"
    }


    async with httpx.AsyncClient() as client:
        r = await client.post(C.post_url, json=json_data, headers=headers)

        if r.status_code != 200:
            print(f"error! can not post to: {C.post_url}")

#---------------------------------------------------------------------------

@sio.event
async def connect(sid, environ):
    sio_debug and print(sid, "connected")

@sio.event
async def sync_hello_connect(sid, data):
    sio_debug and print(data)


@sio.event
async def disconnect(sid):
    sio_debug and print(sid, "disconnected")

# -------------------------------------------------------------------------

@sio.event
async def a_pydal_msg(sid, data):
    print(data)

@sio.event
async def a_pgs_reload(sid, data):
    print(data)

# -----------------------------------------------------------------------------------------------


if __name__ == "__main__":
    # https://www.fatalerrors.org/a/uvicorn-a-lightweight-and-fast-python-asgi-framework.html
    # uvicorn.run(app=app, host="127.0.0.1", port=5000, log_level="info")
    uvicorn.run(
        app=C.SERV_APP_FILE,
        host=C.sio_HOST,
        port=C.sio_PORT,
        reload=True,
        log_level='critical', # 'critical', 'error', 'warning', 'info', 'debug', 'trace'.
        workers=1,
        debug=False,
    )
