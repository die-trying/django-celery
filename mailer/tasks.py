from elk.celery import app as celery


@celery.task
def send_email(owl):
    owl.msg.send()
