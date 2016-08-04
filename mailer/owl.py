from django.conf import settings
from mail_templated import EmailMessage

from mailer.tasks import send_email


class Owl():
    """
    Owl is an email agent. It utilizes default send_mail() as a message-backend,
    hoping you have configured it properly. On the production host it tries to
    queue your message via the Celery daemon.

    For usage examples please see tests.
    """
    def __init__(self, template, ctx, from_email=None, to=[]):
        if from_email is None:
            from_email = settings.EMAIL_NOTIFICATIONS_FROM

        self.template = template
        self.ctx = ctx
        self.to = to
        self.from_email = from_email
        self.EmailMessage()

    def EmailMessage(self):
        """
        This method preventively renders a message to catch possible errors in the
        main flow.
        """
        self.msg = EmailMessage(
            self.template,
            self.ctx,
            self.from_email,
            self.to
        )
        self.msg.render()

    def send(self):
        """
        On the production host — run through celery
        """
        if settings.EMAIL_ASYNC:
            self.msg.send()
        else:
            self.queue()

    def queue(self):
        send_email.delay(self.template, self.ctx, self.from_email, self.to)
