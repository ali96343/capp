#!/usr/bin/env python3

import click, colorama, time
import os, time, sys, subprocess

script_name = os.path.basename(__file__)

__author__ = "Alex Beskopilny"
__copyright__ = f"Copyright 2021, {script_name}: celery-socketio tasks loader for py4web app"
__credits__ = ["Alex Beskopilny"]
__license__ = "MIT"
__version__ = "03.10.2021"  # ver 01 
__maintainer__ = "Alex Beskopilny"
__email__ = "ab96343@gmail.com"
__status__ = "Dev"




this_dir = os.path.dirname(__file__)
if not this_dir in sys.path:
    sys.path.insert(0, this_dir)

import chan_conf as C


# ------------------- utils --------------------
def run_cmd_list(cmd_list):
    my_env = os.environ.copy()
    if isinstance( cmd_list, list ):
        [subprocess.Popen(e.strip().split(), env=my_env ) for e in cmd_list]
    if isinstance( cmd_list, dict ):
        [subprocess.Popen(v.strip().split(), env=my_env ) for k,v in cmd_list.items()]

def shed2list():

    res = []
    for file in os.listdir(C.cel_shed_dir):
        if file.startswith(C.cel_shed_pref):
            res.append(os.path.join(C.cel_shed_dir, file))
    return res

def rm_shed( flist  ):
    for e in flist:
       try:
          os.remove(e)
       except OSError:
          pass
    return True

def to_str(some):
    if isinstance(some, (bytes, bytearray)):
        return some.decode("utf-8")
    return some


def run_command(command="ls"):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()


def kill_pids(pids):
    if pids:
        [run_command(command=f"kill -9 {p}") for p in pids   if os.path.exists(f'/proc/{p}') ]
    return True

def check_external():
    for e in ['ps', 'fuser', 'celery' , 'redis-server' ] :
       res =run_command (f'which {e}') 
       if res == b'':
           click.echo (f'can not find {e}!')
           sys.exit(f'stop! bad env: please, install {e}')


def name2pids(name):
    output = subprocess.Popen(["ps", "ax"], stdout=subprocess.PIPE).stdout.readlines()
    name_binary = name.encode("utf-8")
    myps = [e.strip().split() for e in output if name_binary in e]
    bpids = [p for e in myps for i, p in enumerate(e) if i == 0]
    pids = [to_str(e) for e in bpids]
    return pids


def port2pids(port):
    output = subprocess.Popen(
        ["fuser", f"{port}/tcp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.readlines()
    if output: 
        return [to_str(e) for e in to_str(output[0]).strip().split()]
    return []

def ifOpenClose():
     if C.isOpen(C.sio_HOST, C.sio_PORT):
        port_pids = port2pids(C.sio_PORT)
        kill_pids( port_pids  )
        time.sleep(0.5)
        if C.isOpen(C.sio_HOST, C.sio_PORT):
            return False
     return True

def get_task_files(pattern):
    res = []
    for file in os.listdir(C.cel_shed_dir):
        if file.startswith(C.cel_shed_pref):
            res.append(os.path.join(C.cel_shed_dir, file))
    return res

# ---------------------------------------------


class App:
    def test_env(Z,):

        plist = this_dir.split(os.sep)

        if not sys.platform.startswith("linux"):
            click.echo("it's linux-program !!!")
            sys.exit('stop!')
        if any([plist[-2] != C.P4W_APP, plist[-3] != C.APPS_DIR,]):
            click.echo("bad app name, apps dir ...%s" % plist)
            sys.exit("stop! bad env")
            return False
        check_external()

        p4w_dir = "/".join(this_dir.split(os.sep)[:-3])
        os.chdir(p4w_dir)
        return "ok"

    def find_celery(Z,):
        return name2pids(f"{C.P4W_APP}.{C.cel_files_pre}")

    def find_worker(Z,):
        return name2pids(f"{C.P4W_APP}.celery_stuff worker")

    def find_beat(Z,):
        return name2pids(f"{C.P4W_APP}.celery_stuff beat")

    def find_celery_stuff(Z,):
        return name2pids("celery")

    def find_chan_sio(Z,):
        #return  port2pids(C.sio_PORT)

        if C.isOpen(C.sio_HOST, C.sio_PORT):
            port_pids = port2pids(C.sio_PORT)
            pids = name2pids(f"{C.P4W_APP}/chan_sio")
            for e in pids:
                if e in port_pids:
                    return port_pids
            click.echo(f"not chan_sio works on {C.sio_PORT}/tcp")
            return pids
        return []

    def __init__(Z, silent=False):
        Z.silent = silent
        Z.env_ok = Z.test_env()
        Z.celery_pids = Z.find_celery()
        #Z.worker = Z.find_worker()
        #Z.beat = Z.find_beat()
        Z.celery_stuff_pids = Z.find_celery_stuff()
        Z.chan_sio_pids = Z.find_chan_sio()
        Z.py4web = name2pids("py4web")
        Z.redis = name2pids("redis-server")
        Z.shed_files = shed2list()
        Z.sio_open = 'open'  if C.isOpen(C.sio_HOST, C.sio_PORT) else 'close'
        Z.p4w_open = 'open'  if C.isOpen(C.p4w_host, C.p4w_port) else 'close'

    def stop(Z,):
        kill_pids(Z.celery_pids)
        kill_pids(Z.chan_sio_pids)
        rm_shed( Z.shed_files)
        if ifOpenClose() == False:
           echo.click('can not close sio port')

    def loader(Z,):
      from collections import OrderedDict
      od = {}
      chan_sio_ok = False
      save_num =0
      cmd = ''
      for e in os.listdir(this_dir):
          if e.startswith( C.cel_files_pre, ):
            x= [str(s) for s in e if s.isdigit()]
            y=''
            try:
                y = int( ''.join(x) )
                if save_num < y:
                    save_num = y
            except Exception as ex:
                print(sys.exc_info() )
                print(  f'need unique integer in file name {e}' )
                sys.exit('stop!')
            z = str(y)
            cmd = f'celery -A {C.APPS_DIR}.{C.P4W_APP}.{C.cel_files_pre}{z} worker -Q {C.cel_queue_pre}{z} -B -s {C.shed_path}-{z}'  
            od[y] = cmd
            
          elif e.startswith( 'chan_sio' ):
                chan_sio_ok = True

      if chan_sio_ok:
            cmd = f"python {C.APPS_DIR}/{C.P4W_APP}/chan_sio.py &"
            save_num += 1
            od[  save_num ] =cmd
            #od[  0 ] =cmd
      return od 

    def restart(Z,):
        ifOpenClose()
        if len( Z.redis ) ==0 :
            click.echo( 'run redis-server, pls !'  )
            sys.exit('stop! need redis-server')
        cmds = Z.loader()
        run_cmd_list( cmds )
    
    def kill_all_celery(Z,):
        kill_pids( Z.celery_stuff_pids )
        return True

    def report(Z,):
        if Z.silent:
            return
        click.echo(f"app {C.P4W_APP}, {C.sio_HOST}:{C.sio_PORT} {Z.sio_open}, {C.p4w_host}:{C.p4w_port} {Z.p4w_open}"  )
        click.echo("apps_dir: %s " % C.APPS_DIR)
        click.echo("env: %s " % Z.env_ok)
        click.echo("cel_ pids: %s" % Z.celery_pids)
        click.echo("chan_sio pids: %s %s" %( Z.chan_sio_pids, Z.sio_open) )
        click.echo("py4web pids: %s" % Z.py4web)
        click.echo("redis-server pids: %s" % Z.redis)
        click.echo(f'{C.P4W_APP} shed_files: {len(Z.shed_files)}'  )
        if len(Z.redis) ==0:
              click.echo( 'redis-server: not running!' )
        if len(Z.py4web) == 0:
              click.echo( 'py4web: not running' )
        if len(Z.celery_pids) == 0 or len( Z.chan_sio_pids )==0:
              click.echo( ' --- channel not running: python run-sio.py  ---' ) 
        if len(Z.celery_stuff_pids) >  len(Z.celery_pids):
              click.echo( ' --- multiple celery_stuff.py ? ---' ) 
              click.echo( "celery in memory: %s" % Z.celery_stuff_pids  )
       


# ---------------------------------------------


@click.command()
@click.option(
    "--restart", "-r", is_flag=True, help=f"{C.P4W_APP} restart celery & chan_sio"
)
@click.option(
    "--stop", "-s", is_flag=True, help=f"{C.P4W_APP} stop celery & chan_sio if running"
)
@click.option(
    "--kill_celery", "-kc", is_flag=True, help=f"killall celery"
)
def cli_main(restart, stop, kill_celery):

    """
    celety and socketio tasks loader for py4web app\n
    expected: celery tasks files in special format\n
    expected: sio tasks in chan_sio.py\n 
    expected: running redis-server and py4web server\n 
    config: chan_conf.py\n
    socketio: chan_sio.py\n
    """

    app = App()

    if restart:
        app.stop()
        app.restart()
        click.echo("restarted" )
    elif stop:
        print("stoped")
        app.stop()
    else:
        app.report()

    if kill_celery:
       app.kill_all_celery()  
       click.echo( "all celery pids: %s" %  name2pids( 'celery' ) )


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli_main()
