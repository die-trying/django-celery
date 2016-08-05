from django.dispatch import receiver

from hub.models import Class
from hub.signals import class_scheduled, class_starting_teacher, class_starting_student
from mailer.owl import Owl


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
        to=[c.customer.user.email],
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
        to=[c.customer.user.email],
    )
    owl.send()
