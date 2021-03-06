#!/usr/bin/env python


#--------------------------------------------------------------------------------
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

#--------------------------------------------------------------------------------


import socketio

#sio = socketio.Client()
sio = socketio.Client(logger=True, engineio_logger=True)
cprint('Created socketio client', 'yellow')

@sio.event
def connect():
    print('connected to server')

@sio.event
def disconnect():
    print('disconnected from server')

siostr='http://localhost:6000'

cprint ( siostr , 'yellow' )

sio.connect(siostr, namespaces=['/','/chat', '/test'])
#sio.connect('http://localhost:6000/test/', namespaces=['/','/chat', '/test'])
#sio.connect('http://localhost:6000/socket.io/', namespaces=['/','/chat', '/test'])
#sio.emit("py4web_echo", 'xxxxxxxxxxxxxx')
#sio.wait()

