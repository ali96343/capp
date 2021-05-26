from py4web import action, request, response, abort, redirect, URL, Field
from yatl.helpers import A, DIV, P
from py4web.core import Template
from py4web.utils.form import Form, FormStyleBulma, FormStyleDefault
from json import dumps
from .settings import APP_NAME


# src: https://github.com/miguelgrinberg/flask-celery-example

from .common import (
    db,
    session,
    T,
    cache,
    auth,
    logger,
    authenticated,
    unauthenticated,
    flash,
)


from .celery_stuff import long_task, my_background_task, send_async_email
from .celery_stuff import app as celery_app


@action("index", method=["GET", "POST"])
@action.uses(db, session, T, Template("index.html", delimiters="[[ ]]"))
@unauthenticated("index", "index.html")
def index():
    user = auth.get_user()
    ctrl_template_url = "'" + URL("longtask") + "'"

    hello_message = T("Hello {first_name}".format(**user) if user else "Hello")
    err_message = []

    email_to = "email"
    # email_body = "mytext"
    # email_subj = 'subject'
    send_mode = "mode"

    email_form = Form(
        [
            Field(email_to, label="send email to", default="nil@nil.com"),
            # Field(email_subj, label="email text"),
            # Field(email_body, label="email text"),
            Field(send_mode, "boolean", label="send right away/send in one minute"),
        ],
        formstyle=FormStyleDefault,
        submit_value="Send",
    )

    if email_form.accepted:
        print(email_form.vars[email_to])
        # print(email_form.vars[email_subj])
        # print(email_form.vars[email_body])
        print(email_form.vars[send_mode])

        email_data = {
            "subject": "Hello from py4web",
            "to": email_form.vars[email_to],
            "body": "This is a test email sent from a background Celery task.",
        }

        if email_form.vars[send_mode] == True:
            # send right away
            send_async_email.delay(email_data)
        else:
            # send in one minute
            send_async_email.apply_async(args=[email_data], countdown=60)

    elif email_form.errors:
        err_message.append(email_form.errors)
        print(err_message)

    return locals()


@action("longtask", method=["POST"])
def longtask():
    task = long_task.apply_async()
    response.status = 202
    response.content_type = "application/json"
    response.set_header("Location", URL(f"taskstatus/{task.id}"))
    return dumps({})


@action("taskstatus/<task_id:path>")
def taskstatus(task_id=None):
    task = long_task.AsyncResult(task_id)
    if task.state == "PENDING":
        res = {"state": task.state, "current": 0, "total": 1, "status": "Pending..."}
    elif task.state != "FAILURE":
        res = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": task.info.get("total", 1),
            "status": task.info.get("status", ""),
        }
        if "result" in task.info:
            res["result"] = task.info["result"]
    else:
        # something went wrong in the background job
        res = {
            "state": task.state,
            "current": 1,
            "total": 1,
            "status": str(task.info),  # this is the exception raised
        }
    response.content_type = "application/json"
    return dumps(res)
