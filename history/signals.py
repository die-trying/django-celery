from django.db.models.signals import post_save
from django.dispatch import receiver

from history.models import PaymentEvent
from hub.models import ActiveSubscription, Class


@receiver(post_save, sender=Class, dispatch_uid='Log_single_class_buy')
def log_bought_class(sender, **kwargs):
    """
    Log a fresh-bought class. Logs only single-bought classes. Classes bought
    by subscription are logged by another listener.

    For this signal to work, you should store a `request` property in the sender
    model. For examples, see tests of the hub app. While testing this property
    is usually mocked by elk.utils.mockers.mock_request function.
    """
    if not kwargs['created']:  # log only new classes
        return

    instance = kwargs['instance']

    if instance.buy_source != 0:  # log only single-bought classes
        return

    ev = PaymentEvent(
        customer=instance.customer,
        product=instance,
        price=instance.buy_price,
    )
    ev.request = instance.request  # instance request should be stored by a view

    ev.save()


@receiver(post_save, sender=ActiveSubscription, dispatch_uid='Log_subscription_buy')
def log_bought_subscription(sender, **kwargs):
    """
    Log a fresh-bought subscription
    """
    if not kwargs['created']:  # log only new subscriptions
        return

    instance = kwargs['instance']

    ev = PaymentEvent(
        customer=instance.customer,
        product=instance,
        price=instance.buy_price,
    )
    ev.request = instance.request  # instance request should be stored by a view

    ev.save()
