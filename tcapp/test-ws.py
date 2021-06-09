#!/usr/bin/env python

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


from websocket import create_connection

# pip install websocket-client


HOST = "localhost"
PORT = "6000"


def short_lived_connection():

    wsstr = f"ws://{HOST}:{PORT}/"
    cprint(wsstr)
    ws = create_connection(wsstr)
    # ws = create_connection("ws://localhost:6000/")
    print("1. Sending: 'Hello Server'...")
    ws.send("Hello, Server")
    print("Sent")
    print("2. Receiving...")
    result = ws.recv()
    print("Received: '%s'" % result)
    ws.close()


if __name__ == "__main__":

    short_lived_connection()
