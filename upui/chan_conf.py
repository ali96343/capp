import sys, os, socket

sio_debug = True

values = {
    "slider1": 25,
    "slider2": 0,
    "counter": 100,  # to be continued
    "data_str": ":)",
}


r_url = "redis://"
sio_PORT = 3000
sio_HOST = "127.0.0.1"


sio_serv_url =  f"http://{sio_HOST}:{sio_PORT}" 

P4W_APP = os.path.abspath(__file__).split(os.sep)[-2]

sio_room = f'{P4W_APP}_room'
sio_channel = f"sio_{P4W_APP}"
sio_namespaces= ['/','/test','/chat']
# https://habr.com/ru/post/243791/

post_url = f"http://127.0.0.1:8000/{P4W_APP}/sio_chan_post"

BROADCAST_SECRET = "123secret"
POST_SECRET = "321secret"

SERV_APP_FILE = "chan_sio:app"

# ---------------------------------------------------------

def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False

def check_sio(h=sio_HOST, p=sio_PORT):
    return isOpen( h,p )

# --------------------------------------------------------

def inject_load():
    if sys.platform.startswith('linux'):
        with open('/proc/loadavg', 'rt') as f:
            load = f.read().split()[0:3]
    else:
        load = [int(random.random() * 100) / 100 for _ in range(3)]
    return  load[0],  load[1], load[2]


