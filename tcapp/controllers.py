from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, DIV, P
from py4web.core import bottle
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash



# https://testdriven.io/blog/asynchronous-tasks-with-falcon-and-celery/

@unauthenticated("index", "index.html")
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    menu = DIV(
               P( "test: celery + websocket + tornado"),
               A( "celery + ws + tronado", _role="button", _href=URL('to_tornado_celery',   ),) ,
               A( "to ok2", _role="button", _href=URL('to_ws_tornado',   ),) ,
              )
    return dict(message=message, menu=menu)



@action("to_tornado_celery")
def to_tornado_celery():
    location='http://localhost:8888'
    bottle.response.status = 303
    bottle.response.set_header("Location", location)

    return 'ok2'


@action("to_ws_tornado")
def to_ws_tornado():
    print ('ws')
    return 'ok2'
   
