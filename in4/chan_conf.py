import sys, os, socket, re
import requests


import sys

sio_debug = False

p4w_host = '127.0.0.1'
p4w_port = '8000'

sio_PORT = 5000 
sio_HOST = p4w_host 


P4W_APP = os.path.dirname( os.path.abspath(__file__) ).split(os.sep)[-1]
APPS_DIR = os.path.dirname( os.path.abspath(__file__) ).split(os.sep)[-2]


r_url = "redis://"

sio_serv_url =  f"http://{sio_HOST}:{sio_PORT}" 
sse_url = f"http://{sio_HOST}:{sio_PORT}/pydalsse" 
sse_get_data = f"http://{p4w_host}:{p4w_port}/{P4W_APP}/lorem_get" 



sio_room = f'{P4W_APP}_room'
sio_channel = f"sio_{P4W_APP}"
sio_namespaces= ['/','/test','/chat']

post_url = f"http://{p4w_host}:{p4w_port}/{P4W_APP}/sio_chan_post"

BROADCAST_SECRET = "123secret"
POST_SECRET = "321secret"

SERV_APP_FILE = "chan_sio:app"
SIO_FILE=SERV_APP_FILE.split(':')[0] + '.py'

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
    
    if not isOpen( p4w_host, p4w_port ):
        return 'p4w not running!?'

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

def cprint(mess="mess", color="green"):
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

# ------------- celery stuff conf  --------------------------
def get_name_num(fnm):
    bfnm =  os.path.basename(fnm)
    mod_nm = os.path.splitext(bfnm)[0]
    x= [str(s) for s in bfnm if s.isdigit()]
    y=''.join(x)
    try:
       return int( y), str(mod_nm)
    except Exception as ex:
       print(sys.exc_info() )
       print(  f'bad celery file name {fnm}, need number' )
       raise

# ----------------------------------------------------------

cel_shed_dir='/tmp'
cel_shed_pref=f'xshed.{P4W_APP}-'
shed_path=os.path.join( cel_shed_dir, cel_shed_pref  )
cel_files_pre='xcel_'
cel_queue_pre=cel_files_pre #   'que'


# --------------------------------
