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
