#!/usr/bin/env python3

# While this code still works, I would recommend using Fast API for websockets in modern applications.
# See: https://fastapi.tiangolo.com/advanced/websockets/

# Note this is targeted at python 3

# --------------------------------------------------------------------------------
import sys


def cprint(mess="mess", color="green"):
    # https://www.geeksforgeeks.org/print-colors-python-terminal/
    c_fmt = "--- {}"
    if sys.stdout.isatty() == True:
        c = {
            "red": "\033[91m {}\033[00m",
            "green": "\033[92m {}\033[00m",
            "yellow": "\033[93m {}\033[00m",
            "cyan": "\033[96m {}\033[00m",
            "gray": "\033[97m {}\033[00m",
            "purple": "\033[95m {}\033[00m",
        }
        c_fmt = c.get(color, c_fmt)
    print(c_fmt.format(mess))
    return mess


# --------------------------------------------------------------------------------

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.websocket
import tornado.options
import time

ws_debug = True

LISTEN_PORT = 6000
LISTEN_ADDRESS = "127.0.0.1"

import tornado.websocket
import time, urllib
from tornado.httputil import url_concat
import tornado.httpclient

ws_debug = True

# https://github.com/miguelgrinberg/python-socketio/issues/201


class BaseHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        cprint("setting headers!!!", 'yellow')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def post(self):
        self.write("some post")

    def get(self):
        self.write("some get")

    def options(self):
        # no body
        self.set_status(204)
        self.finish()


class WsHandler(tornado.websocket.WebSocketHandler, BaseHandler):
    def simple_init(self):
        self.last = time.time()
        self.stop = False

    def open(self):
        #    client opens a connection
        self.simple_init()
        ws_debug and print(f"ws: {time.time() - self.last:.1f}: New client connected")
        self.write_message(f"ws: {time.time() - self.last:.1f}: You are connected")

    def on_message(self, message):
        #    Message received on the handler
        ws_debug and print(
            f"Echo from ws: {time.time() - self.last:.1f}: received message {message}"
        )
        self.write_message(
            f"Echo from ws: {time.time() - self.last:.1f}: You said - {message}"
        )
        self.last = time.time()

    def on_close(self):
        #    Channel is closed
        ws_debug and print(f"ws: {time.time() - self.last:.1f}: connection is closed")
        self.stop = True

    def check_origin(self, origin):
        cprint ('Ws check_origin', 'yellow')
        return True


import socketio

sio_debug = False
sio = socketio.AsyncServer(async_mode="tornado")


@sio.event
async def connect(sid, environ):
    sio_debug and print("sio: connect ", sid)


@sio.event
async def disconnect(sid):
    sio_debug and print("sio: disconnect ", sid)


@sio.on("to_py4web")
async def echo(sid, data):
    sio_debug and print("sio: from client: ", data)
    sio.emit("py4web_echo", data)


_Handler = socketio.get_tornado_handler(sio)


class SioHandler(_Handler, BaseHandler):
    def check_origin(self, origin):
        cprint ('Sio check_origin', 'yellow')
        return True


def main():

    app = tornado.web.Application([(r"/", WsHandler), (r"/socket.io/", SioHandler)])

    # Setup HTTP Server
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(LISTEN_PORT, LISTEN_ADDRESS)

    from tornado.log import enable_pretty_logging

    enable_pretty_logging()

    # Start IO/Event loop
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    sys.exit(main() )
