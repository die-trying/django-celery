import pytz
from django.utils import timezone
from mail_templated import EmailMessage

from elk.celery import app as celery


@celery.task
def send_email(*args, **kwargs):
    """
    Send queued message. We hope that errors are checked in the main thread.

    TODO: use the decorator from owl.py
    """
    old_tz = None
    headers = kwargs.get('headers')
    if headers is not None and headers.get('X-ELK-Timezone') and headers['X-ELK-Timezone'] != 'None':
        old_tz = timezone.get_current_timezone()
        timezone.activate(pytz.timezone(headers['X-ELK-Timezone']))

    msg = EmailMessage(*args, **kwargs)
    msg.send()

    if old_tz is not None:
        timezone.activate(old_tz)
