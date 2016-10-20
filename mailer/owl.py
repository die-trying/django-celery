import pytz
from django.conf import settings
from django.utils import timezone, translation
from mail_templated import EmailMessage

from elk.logging import logger
from mailer.tasks import send_email


def user_tz(fn):
    def wrapper(*args, **kwargs):
        old_tz = None
        self = args[0]

        if self.timezone is not None:  # store the old timezone
            old_tz = timezone.get_current_timezone()
            timezone.activate(self.timezone)

        res = fn(*args, **kwargs)  # call the actual function

        if old_tz is not None:  # restore the timezone
            timezone.activate(old_tz)

        return res
    return wrapper


def disable_i18n(fn):
    def wrapper(*args, **kwargs):
        with translation.override(None):
            return fn(*args, **kwargs)

    return wrapper


class Owl():
    """
    Owl is an email agent. It utilizes default send_mail() as a message-backend,
    hoping you have configured it properly. On the production host it tries to
    queue your message via the Celery daemon.

    For usage examples please see tests.
    """

    timezone = None

    def __init__(self, template, ctx, from_email=None, timezone=None, to=[]):
        if from_email is None:
            from_email = settings.EMAIL_NOTIFICATIONS_FROM

        self.template = template
        self.ctx = ctx
        self.to = to
        self.from_email = from_email

        if timezone is not None:
            if isinstance(timezone, str):
                self.timezone = pytz.timezone(timezone)
            else:
                self.timezone = timezone

        self.headers = {
            'X-ELK-Timezone': str(self.timezone),
        }

        self.EmailMessage()

    @user_tz
    @disable_i18n
    def EmailMessage(self):
        """
        This method preventively renders a message to catch possible errors in the
        main flow.
        """
        self.msg = EmailMessage(
            self.template,
            self.ctx,
            self.from_email,
            self.to,
            headers=self.headers,
            reply_to=[settings.REPLY_TO],
        )
        self.msg.render()

    @user_tz
    @disable_i18n
    def send(self):
        """
        Send message

        On the production host uses celery, on dev — django configured backend.
        """
        if not self.clean():
            logger.warning('Trying to send invalid message!')
            return

        if not settings.EMAIL_ASYNC:
            self.msg.send()
        else:
            self.queue()

    @user_tz
    @disable_i18n
    def queue(self):
        self.headers['X-ELK-Queued'] = 'True'
        send_email.delay(owl=self)

    def attach(self, filename=None, content=None, mimetype=None):
        """
        Add an attachment to the message

        See http://django-mail-templated.readthedocs.io/en/master/api.html?highlight=attach#mail_templated.EmailMessage.attach
        """
        return self.msg.attach(filename, content, mimetype)

    def clean(self):
        if not self.to or not self.to[0]:
            return False

        return True
