from django.conf import settings
from django.dispatch import Signal, receiver

from mailer.owl import Owl

new_user_registered = Signal(providing_args=['user', 'whom_to_notify'])  # class is just scheduled


@receiver(new_user_registered, dispatch_uid='new_user_notify')
def new_user_notify(sender, **kwargs):
    whom_to_notify = kwargs.get('whom', settings.SUPPORT_EMAIL)

    user = kwargs['user']
    owl = Owl(
        template='mail/service/new_user.html',
        ctx={
            'user': user,
        },
        to=[whom_to_notify],
        from_email='%s <%s>' % (user.crm.full_name, user.email)
    )
    owl.send()
