import sys, os
sys.path.append(os.path.abspath('./'))  # == sys.path.append(os.path.abspath('/home/w3p/set1/py4web'))


# https://stackoverflow.com/questions/30753040/retrieve-task-result-by-id-in-celery


from apps.capp.celery_stuff import serve_a_beer # Importing the task

res = serve_a_beer( 'weiss', '500ml' )
#print ('res.status: ',res.status)
#print ('res.id: ',res.id)





from celery.result import AsyncResult
from apps.capp.celery_stuff import app


if res:
   res_res = AsyncResult( res.id   ,app=app)

   print(res_res.state) # 'SUCCESS'
   print(res_res.get()) # 7

