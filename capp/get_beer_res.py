import sys, os
sys.path.append(os.path.abspath('./'))  # == sys.path.append(os.path.abspath('/home/w3p/set1/py4web'))


# https://stackoverflow.com/questions/30753040/retrieve-task-result-by-id-in-celery


from apps.capp.celery_stuff import serve_a_beer # Importing the task

res = serve_a_beer( 'weiss', '500ml' )
#print ('res.status: ',res.status)
#print ('res.id: ',res.id)


# https://overcoder.net/q/935361/%D0%BF%D0%BE%D0%BB%D1%83%D1%87%D0%B8%D1%82%D1%8C-%D1%80%D0%B5%D0%B7%D1%83%D0%BB%D1%8C%D1%82%D0%B0%D1%82-%D0%B8%D0%B7-taskid-%D0%B2-celery-%D0%B8%D0%B7-%D0%BD%D0%B5%D0%B8%D0%B7%D0%B2%D0%B5%D1%81%D1%82%D0%BD%D0%BE%D0%B3%D0%BE-%D0%B7%D0%B0%D0%B4%D0%B0%D0%BD%D0%B8%D1%8F



from celery.result import AsyncResult
from apps.capp.celery_stuff import app


if res:
   res_res = AsyncResult( res.id   ,app=app)
   print (res.status)
   print (res_res.status)

   print(res_res.state) # 'SUCCESS'
   print(res_res.get()) # 7 res_res.result

