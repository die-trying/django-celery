from elk.celery import app as celery
from market.models import Class


@celery.task
def mark_classes_as_fully_used():
    for i in Class.objects.to_be_marked_as_used():
        i.mark_as_fully_used()
