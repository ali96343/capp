import sys, os, socket
import requests

sio_debug = True

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

# ------  UTILS ----------------------------------------

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


def inject_load():
    if sys.platform.startswith('linux'):
        with open('/proc/loadavg', 'rt') as f:
            load = f.read().split()[0:3]
    else:
        load = [int(random.random() * 100) / 100 for _ in range(3)]
    return  load[0],  load[1], load[2]


def sync_event_post(event_name, data=None, room=None, post=True):

    json_data = {
          "event_name": event_name,
          "data": data,
          "room": room,
          "broadcast_secret": BROADCAST_SECRET,
    }

    headers_dict = {'Content-type': 'application/json', 'Accept': 'text/plain',
                    "app-param": 'some-param' }
    try:
       x = requests.post(post_url, json=json_data, headers=headers_dict)
    except Exception as ex:
        print ('sync_event_post: ',ex )
        print(sys.exc_info())
        return 'bad'
 

    if x.status_code != 200:
        print(f"error! can not post to: {post_url}")


