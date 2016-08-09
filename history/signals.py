from django.db.models.signals import post_save
from django.dispatch import receiver

from history.models import PaymentEvent
from hub.models import Class, Subscription


@receiver(post_save, sender=Class, dispatch_uid='Log_single_class_buy')
def log_bought_class(sender, **kwargs):
    """
    Log a fresh-bought class. Logs only single-bought classes. Classes bought
    by subscription are logged by another listener.

    For this signal reciever to work, you should store a `request` property in
    the sender model. For examples, see tests of this app.
    """
    if not kwargs['created']:  # log only new classes
        return

    instance = kwargs['instance']

    if not hasattr(instance, 'request'):  # if we don't know a request, probably it's testing
        return

    if instance.buy_source != 'single':  # log only single-bought classes
        return

    ev = PaymentEvent(
        src='customer',  # flex scope: in future you should acknowledge — who has added a class: staff or a student himself
        customer=instance.customer,
        product=instance,
        price=instance.buy_price,
    )
    ev.request = instance.request  # instance request should be stored by a view

    ev.save()


@receiver(post_save, sender=Subscription, dispatch_uid='Log_subscription_buy')
def log_bought_subscription(sender, **kwargs):
    """
    Log a fresh-bought subscription.

    For this signal reciever to work, you should store a `request` property in
    the sender model. For examples, see tests of this app.
    """
    if not kwargs['created']:  # log only new subscriptions
        return

    instance = kwargs['instance']

    if not hasattr(instance, 'request'):  # if we don't know a request, probably it's testing
        return

    ev = PaymentEvent(
        src='customer',  # flex scope: in future you should acknowledge — who has added a subscription: staff or a student himself
        customer=instance.customer,
        product=instance,
        price=instance.buy_price,
    )
    ev.request = instance.request  # instance request should be stored by a view

    ev.save()
