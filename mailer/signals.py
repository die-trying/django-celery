from django.dispatch import receiver

from hub.models import Class
from hub.signals import class_scheduled
from mailer.owl import Owl


@receiver(class_scheduled, sender=Class, dispatch_uid='notify_student')
def notify_student(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mailer/class/scheduled_user.html',
        ctx={
            'c': c,
        },
        to=[c.customer.user.email],
    )
    owl.send()


@receiver(class_scheduled, sender=Class, dispatch_uid='notify_teacher')
def notify_teacher(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mailer/class/scheduled_teacher.html',
        ctx={
            'c': c,
        },
        to=[c.customer.user.email],
    )
    owl.send()
