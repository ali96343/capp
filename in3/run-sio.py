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




this_dir = os.path.dirname( os.path.abspath(__file__) )
if not this_dir in sys.path:
    sys.path.insert(0, this_dir)

import chan_conf as C


# ------------------- utils --------------------
def run_cmd_list(cmd_list):
    my_env = os.environ.copy()
    if isinstance( cmd_list, dict ):
        [subprocess.Popen(v.strip().split(), env=my_env ) for k,v in cmd_list.items()]
        return
    if isinstance( cmd_list, list ):
        [subprocess.Popen(e.strip().split(), env=my_env ) for e in cmd_list]
    return

def shed2list():

    res = []
    common_shed = []
    for file in os.listdir(C.cel_shed_dir):
        if file.startswith(C.cel_shed_pref):
            res.append(os.path.join(C.cel_shed_dir, file))
        if file.startswith(C.cel_shed_common_pref):
            common_shed.append(os.path.join(C.cel_shed_dir, file))
    sio_ports=set()
    for e in common_shed:
         sio_ports.add(e.split('.')[1])
    #if len (res) != len( common_shed ):
    #     print ( '+++ common shed files esxis! ',common_shed )
    #print ( 'all sio_ports: ', sio_ports )
    return res, common_shed , sio_ports

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
        [run_command(command=f"kill -9 {p}") for p in pids if os.path.exists(f'/proc/{p}') ]
    return True

def check_external():
    for e in ['ps', 'fuser', 'celery' , 'redis-server' ] :
       res =run_command (f'which {e}') 
       if res == b'':
           click.echo (f'can not find {e}!')
           sys.exit(f'stop! bad env: please, install {e}, or set $PATH')


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
     # check_sio_tcp ()
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
        if any([plist[-1] != C.P4W_APP, plist[-2] != C.APPS_DIR,]):
            click.echo("bad app name, apps dir ...%s" % plist)
            sys.exit("stop! bad env")
            return False
        check_external()

        p4w_dir = "/".join(this_dir.split(os.sep)[:-2])
        os.chdir(p4w_dir)
        return "ok"

    def find_celery(Z,):
        return name2pids(f"{C.P4W_APP}.{C.cel_files_pre}")

    def find_worker(Z,):
        return name2pids(f"{C.P4W_APP}.celery_stuff worker")

    def find_beat(Z,):
        return name2pids(f"{C.P4W_APP}.celery_stuff beat")

    def find_celery4sio(Z,):

        # /tmp/xshed.3000.xxxxxxxxxx
        # /tmp/xshed.5000.xxxxxxxxxx

        my_celery=[]
        other_celery=[]

        pref_path=set()
        for e in Z.shed_common_files:
             lx = e.split('.')
             pref_path.add ( '.'.join(lx[:2])  )
        #print ( pref_path )

     
        for e in pref_path:
            if str(C.sio_PORT) in e:
                my_celery = name2pids(e )
            else:
                other_celery = name2pids(e )
        #print ('+++ my_celery: ',my_celery )
        #print ('+++ other_celery: ',other_celery )
        #print ('--- ', name2pids("celery") )

        return my_celery + other_celery 
        #return name2pids("celery")

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
        #Z.celery_stuff_pids = Z.find_celery4sio()
        Z.chan_sio_pids = Z.find_chan_sio()
        Z.py4web = name2pids("py4web")
        Z.redis = name2pids("redis-server")
        Z.shed_files, Z.shed_common_files, Z.ports_common = shed2list()
        Z.celery_stuff_pids = Z.find_celery4sio()
        Z.sio_open = 'open'  if C.isOpen(C.sio_HOST, C.sio_PORT) else 'close'
        Z.p4w_open = 'open'  if C.isOpen(C.p4w_host, C.p4w_port) else 'close'

    def stop(Z,):
        kill_pids(Z.chan_sio_pids)
        kill_pids(Z.celery_pids)
        rm_shed( Z.shed_files)
        if ifOpenClose() == False:
           echo.click('can not close sio port')
        shed_port_files = [ e for e in Z.shed_common_files if str(C.sio_PORT) in e ]
        if len( shed_port_files ):
            print ( f'found sio tasks on my port {C.sio_PORT}', shed_port_files   )
            #rm_shed ( shed_port_files )
            #print ( '--- removed shed-files: ', shed_port_files )
               

    def loader(Z,):
      from collections import OrderedDict
      od = {}
      chan_sio_file = False
      cmd = ''
      for e in os.listdir(this_dir):
          if e.startswith( C.cel_files_pre, ):
            x= [str(s) for s in e if s.isdigit()]
            y=''
            try:
                y = int( ''.join(x) )
            except Exception as ex:
                print(sys.exc_info() )
                print(  f'need unique integer in file name {e}' )
                sys.exit('stop!')
            z = str(y)
            if z=='0':
               click.echo('can not use "0" as task number!')
               continue
            cmd = f'celery -A {C.APPS_DIR}.{C.P4W_APP}.{C.cel_files_pre}{z} worker -Q {C.cel_queue_pre}{z} -B -s {C.shed_path}-{z}'  
            od[y] = cmd
            
          elif e.startswith( 'chan_sio' ):
                chan_sio_file = True

      if chan_sio_file:
            cmd = f"python {C.APPS_DIR}/{C.P4W_APP}/{C.SIO_FILE} &"
            od[  0 ] =cmd
      return od 

    def restart(Z,):
        ifOpenClose()
        if len( Z.redis ) ==0 :
            click.echo( 'run redis-server, pls !'  )
            sys.exit('stop! need redis-server')
        cmds = Z.loader()
        run_cmd_list( cmds )
    
    def kill_all_sio(Z,):
        for e in Z.ports_common:
            port_pids = port2pids( e  )
            kill_pids( port_pids )
              #Z.shed_files, Z.shed_common_files, Z.ports_common = shed2list()
        kill_pids( Z.celery_stuff_pids )
        rm_shed( Z.shed_common_files  )
        return True

    def report(Z,):
        if Z.silent:
            return
        click.echo(f"app {C.P4W_APP}, {C.sio_HOST}:{C.sio_PORT} {Z.sio_open}, {C.p4w_host}:{C.p4w_port} {Z.p4w_open}"  )
        click.echo("apps_dir: %s " % C.APPS_DIR)
        click.echo("env: %s " % Z.env_ok)
        #click.echo("cel_pids: %s" % Z.celery_pids)
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
        #if len(Z.celery_stuff_pids) >  len(Z.celery_pids):
        #      click.echo( '--- multiple celery tasks ---' ) 
              #click.echo( "celery in memory: %s" % Z.celery_stuff_pids  )
        if len(Z.ports_common) >1  :
              print ('--- multiple sio tasks: ', Z.ports_common  )  
              #Z.shed_files, Z.shed_common_files, Z.ports_common = shed2list()
       


# ---------------------------------------------


@click.command()
@click.option(
    "--restart", "-r", is_flag=True, help=f"{C.P4W_APP} restart celery & chan_sio"
)
@click.option(
    "--stop", "-s", is_flag=True, help=f"{C.P4W_APP} stop celery & chan_sio if running"
)
@click.option(
    "--killall_sio_and_celery", "-kc", is_flag=True, help=f"killall sio and celery"
)
def cli_main(restart, stop, killall_sio_and_celery):

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
        app.stop()
        click.echo("stoped")
    else:
        app.report()

    if killall_sio_and_celery:
       app.kill_all_sio()  
       click.echo( "all celery pids: %s" %  name2pids( 'celery' ) )


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    cli_main()
