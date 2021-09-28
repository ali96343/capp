#!/usr/bin/env python3

import sys, os

import uvicorn
import socketio
import httpx
import requests

this_dir = os.path.abspath( __file__ )
if not this_dir in sys.path:
    sys.path.insert(0,  this_dir )
import chan_conf as C
#sys.path.pop()


# pip install aioredis==1.3.1

# --------------- global ------------------------------------------

sio_debug = True

sio_debug and print(f"===: {C.SERV_APP_FILE}")

# ----------------------------------------------------------------
r_mgr = socketio.AsyncRedisManager(C.r_url, channel=C.sio_channel,  write_only=False)
sio = socketio.AsyncServer(
    async_mode="asgi",
    client_manager=r_mgr,
    cors_allowed_origins="*",
    SameSite=None,
    logger=True,
    engineio_logger=True,
)
app = socketio.ASGIApp(sio, static_files={"/": "./public/index.html"})

# --------------------------- utils ----------------------------------------------

async def sio_event_post(event_name, data=None, room=None, post=True):

    # https://zetcode.com/python/httpx/

    json_data = {
        "event_name": event_name,
        "data": data,
        "room": room,
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
async def disconnect(sid):
    sio_debug and print(sid, "disconnected")

# -----------------------------------------------------------------------------------------------


if __name__ == "__main__":
    # https://www.fatalerrors.org/a/uvicorn-a-lightweight-and-fast-python-asgi-framework.html
    # uvicorn.run(app=app, host="127.0.0.1", port=5000, log_level="info")
    uvicorn.run(
        app=C.SERV_APP_FILE,
        host=C.sio_HOST,
        port=C.sio_PORT,
        reload=True,
        workers=1,
        debug=False,
    )
