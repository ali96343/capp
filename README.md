## capp - py4web + redis + celery

redis-server must be installed and running

----------------------------------------

0 put capp to py4web/apps/capp

1 run py4web

2 from py4web directory run celery

  celery -A apps.capp.celery_stuff worker --loglevel=info

3 firefox localhost:8000/capp

----------------------------------------

fcapp - py4web app from https://github.com/miguelgrinberg/flask-celery-example

0 put fcapp to py4web/apps/fcapp

1 run py4web

2 celery -A apps.fcapp.celery_stuff worker --loglevel=info

3 firefox localhost:8000/fcapp

----------------------------------------

tcapp - py4web app from https://github.com/dkrichards86/tornado-celery 


(tcapp:  celery + websocket + tornado-second-server(localhost:6000) )


0 put tcapp to py4web/apps/tcapp

1 run py4web

2 cd apps/tcapp/tor_cel

3 celery -A celery_tasks worker -l info &

4 python wssio-server6000.py &

5 firefox localhost:8000/tcapp

---------------------------------------

upui - py4web + socketio + celery + redis

( upui - Dynamically sends a linux-loadavg from /proc/loadavg to html pages every 2 sec and 
updates part of the page without using ajax, sends data to pydal   )


0 put upui to py4web/apps/upui

1 run py4web

2 in other terminal 
  cd py4web

celery -A apps.upui.celery_stuff beat &
celery -A apps.upui.celery_stuff worker -l info

3 in other terminal
  cd py4web/apps/upui 
  ./chan_sio 

4 fierfox localhost:8000/upui

5 also, test pgs_reload with

  curl http://localhost:8000/upui/pgs_reload

  curl http://localhost:8000/upui/sio_pusher


idea from 

https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask

