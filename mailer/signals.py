from django.conf import settings
from django.dispatch import receiver

from acc.signals import new_user_registered
from mailer.owl import Owl
from market.models import Class
from market.signals import class_scheduled, class_starting_student, class_starting_teacher


@receiver(new_user_registered, dispatch_uid='new_user_notify')
def new_user_notify(sender, **kwargs):
    whom_to_notify = kwargs.get('whom', settings.SUPPORT_EMAIL)

    owl = Owl(
        template='mailer/service/new_user.html',
        ctx={
            'user': kwargs['user']
        },
        to=[whom_to_notify],
    )
    owl.send()


@receiver(class_scheduled, sender=Class, dispatch_uid='notify_student_class_scheduled')
def notify_student_class_scheduled(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mailer/class/student/scheduled.html',
        ctx={
            'c': c,
        },
        to=[c.customer.user.email],
    )
    owl.send()


@receiver(class_scheduled, sender=Class, dispatch_uid='notify_teacher_class_scheduled')
def notify_teacher_class_scheduled(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mailer/class/teacher/scheduled.html',
        ctx={
            'c': c,
        },
        to=[c.timeline.teacher.user.email],
    )
    owl.send()


@receiver(class_starting_student, dispatch_uid='notify_class_starting_student')
def class_starting_student(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mailer/class/student/starting.html',
        ctx={
            'c': c,
        },
        to=[c.customer.user.email],
    )
    owl.send()


@receiver(class_starting_teacher, dispatch_uid='notify_class_starting_teacher')
def class_starting_teacher(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mailer/class/teacher/starting.html',
        ctx={
            'c': c,
        },
        to=[c.timeline.teacher.user.email],
    )
    owl.send()
