from django.conf import settings
from django.dispatch import Signal, receiver

from mailer.owl import Owl

unsafe_calendar_update = Signal(providing_args=['instance'])


@receiver(unsafe_calendar_update, dispatch_uid='unsafe_calendar_update_notify')
def unsafe_calendar_update_notify(sender, **kwargs):
    src = kwargs['instance']
    owl = Owl(
        template='mail/service/unsafe_calendar_update.html',
        ctx={
            'teacher': str(src.teacher),
            'previous_events_count': src.previous_events().count(),
            'current_events_count': len(src.events),
            'calendar_name': src._meta.verbose_name,
            'calendar_pk': src.pk,
        },
        to=[settings.SUPPORT_EMAIL],
    )
    owl.send()
