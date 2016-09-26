from django.dispatch import Signal, receiver

from mailer.owl import Owl


class_starting_teacher = Signal(providing_args=['instance'])  # class is about to start (for teachers)
class_starting_student = Signal(providing_args=['instance'])  # class is about to start (for students)
#
# i have made two different signals, because they obviously will require different
# options, like time, left to the lesson


@receiver(class_starting_student, dispatch_uid='notify_class_starting_student')
def notify_class_starting_student(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mail/class/student/starting.html',
        ctx={
            'c': c,
        },
        to=[c.customer.user.email],
        timezone=c.customer.timezone,
    )
    owl.send()


@receiver(class_starting_teacher, dispatch_uid='notify_class_starting_teacher')
def notify_class_starting_teacher(sender, **kwargs):
    c = kwargs['instance']
    owl = Owl(
        template='mail/class/teacher/starting.html',
        ctx={
            'c': c,
        },
        to=[c.timeline.teacher.user.email],
        timezone=c.timeline.teacher.user.crm.timezone,
    )
    owl.send()
