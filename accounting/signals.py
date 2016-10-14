from django.dispatch import receiver

from accounting.models import Event as AccEvent
from market.signals import class_cancelled


@receiver(class_cancelled, dispatch_uid='account_class_cancellation')
def account_class_cancellation(sender, **kwargs):
    if kwargs['src'] != 'customer':
        return

    cancelled_class = kwargs['instance']
    ev = AccEvent(
        originator=cancelled_class,
        teacher=cancelled_class.timeline.teacher,
        event_type='customer_inspired_cancellation',
    )
    ev.save()
