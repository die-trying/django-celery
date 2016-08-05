from mail_templated import EmailMessage
from elk.celery import app as celery


@celery.task
def send_email(template, ctx, from_email, to):
    """
    Send queued message. We hope that errors are checked in the main thread.
    """
    msg = EmailMessage(template, ctx, from_email, to)
    msg.send()
