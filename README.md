## capp - py4web + redis + celery

0 git clone  capp to  py4web/apps/capp

1 run py4web

2 from py4web directory run celery

  celery -A apps.capp.celery_stuff worker --loglevel=info

3 firefox localhost:8000/capp
