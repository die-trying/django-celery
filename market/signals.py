from django.dispatch import Signal, receiver

from mailer.owl import Owl


class_scheduled = Signal(providing_args=['instance'])  # class is just scheduled
class_cancelled = Signal(providing_args=['instance', 'src'])  # class is just cancelled


@receiver(class_scheduled, dispatch_uid='notify_student_class_scheduled')
def notify_student_class_scheduled(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mail/class/student/scheduled.html',
        ctx={
            'c': c,
        },
        to=[c.customer.user.email],
        timezone=c.customer.timezone,
    )
    owl.send()


@receiver(class_scheduled, dispatch_uid='notify_teacher_class_scheduled')
def notify_teacher_class_scheduled(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mail/class/teacher/scheduled.html',
        ctx={
            'c': c,
        },
        to=[c.timeline.teacher.user.email],
        timezone=c.timeline.teacher.user.crm.timezone,
    )
    owl.send()


@receiver(class_cancelled, dispatch_uid='notify_student_class_is_cancelled')
def notify_student_class_is_cancelled(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mail/class/student/cancelled.html',
        ctx={
            'c': c,
            'src': kwargs['src'],
        },
        to=[c.customer.user.email],
        timezone=c.customer.timezone,
    )
    owl.send()


@receiver(class_cancelled, dispatch_uid='notify_teacher_class_is_cancelled')
def notify_teacher_class_is_cancelled(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mail/class/teacher/cancelled.html',
        ctx={
            'c': c,
            'src': kwargs['src'],
        },
        to=[c.timeline.teacher.user.email],
        timezone=c.timeline.teacher.user.crm.timezone,
    )
    owl.send()
