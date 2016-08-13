from datetime import timedelta

from elk.celery import app as celery
from hub.models import Class
from hub.signals import class_starting_student, class_starting_teacher


@celery.task
def notify_15min_to_class():
    for i in Class.objects.starting_soon(timedelta(minutes=30), pre_start_notifications_sent_to_teacher=False):
        i.pre_start_notifications_sent_to_teacher = True
        i.save()
        class_starting_teacher.send(sender=notify_15min_to_class, instance=i)

    for i in Class.objects.starting_soon(timedelta(minutes=30), pre_start_notifications_sent_to_student=False):
        i.pre_start_notifications_sent_to_student = True
        i.save()
        class_starting_student.send(sender=notify_15min_to_class, instance=i)


@celery.task
def mark_classes_as_fully_used():
    for i in Class.objects.to_be_marked_as_used():
        i.mark_as_fully_used()
