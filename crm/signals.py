from django.apps import apps
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from mailer.owl import Owl

trial_lesson_added = Signal()


@receiver(trial_lesson_added, dispatch_uid='notify_new_customer_about_trial_lesson')
def notify_new_customer_about_trial_lesson(sender, **kwargs):
    owl = Owl(
        template='mail/trial_lesson_added.html',
        ctx={
            'c': sender,
        },
        to=[sender.user.email],
        timezone=sender.timezone,
    )
    owl.send()


@receiver(post_save, sender=User, dispatch_uid='create_profile_for_new_users')
def create_profile_for_new_users(sender, **kwargs):
    if not kwargs['created']:
        return

    user = kwargs['instance']
    Customer = apps.get_model('crm.Customer')
    try:
        if user.crm is not None:
            return
    except Customer.DoesNotExist:
        pass

    Customer.objects.create(user=user)
