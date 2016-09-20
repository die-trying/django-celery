from datetime import timedelta

from elk.celery import app as celery
from market.models import Class
from timeline.signals import class_starting_student, class_starting_teacher


@celery.task
def notify_15min_to_class():
    for i in Class.objects.starting_soon(timedelta(minutes=30)):
        if not i.pre_start_notifications_sent_to_teacher:
            i.pre_start_notifications_sent_to_teacher = True
            i.save()
            class_starting_teacher.send(sender=notify_15min_to_class, instance=i)

    for i in Class.objects.starting_soon(timedelta(minutes=30), pre_start_notifications_sent_to_student=False):
        i.pre_start_notifications_sent_to_student = True
        i.save()
        class_starting_student.send(sender=notify_15min_to_class, instance=i)
