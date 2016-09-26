from elk.celery import app as celery
from extevents.models import GoogleCalendar


@celery.task
def update_google_calendars():
    for calendar in GoogleCalendar.objects.active():
        calendar.poll()
        calendar.update()
