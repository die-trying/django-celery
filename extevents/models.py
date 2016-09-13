import datetime

import pytz
import requests
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from icalendar import Calendar


class ExternalEvent(models.Model):
    """
    Represents single External event.

    ext_src is a contentype of the source, that has generated this event,
    for example :model:`extevents.GoogleCalendar`. ext_src should be a subsclass
    of :model:`extevents.ExternalEventSource`.

    """
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='busy_periods')

    ext_src_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'app_label': 'extevents'})
    ext_src_id = models.PositiveIntegerField()
    ext_src = GenericForeignKey('ext_src_type', 'ext_src_id')

    start = models.DateTimeField()
    end = models.DateTimeField()
    description = models.CharField(max_length=140)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('teacher', 'ext_src_type', 'ext_src_id', 'start', 'end')


class ExternalEventSource(models.Model):
    """
    Generic abstract class for an Event source. Subclasses should implement the following:
        * `poll` method that popuates the self.events list
        * Relation to :model:`teachers.Teacher`, called 'teacher'

    Usage:
        # Assuming that teacher is an instance of :model:`teachers.Teacher`

        for calendar in teacher.google_calendars:
            calendar.poll()  # get new events, implemented in subclass
            calendar.update()  # update event database, implemented in this class

    This will clean up previous events and store new ones, fetched by the model:`extevents.GoogleCalendar`.poll() method.

    """
    url = models.URLField()
    active = models.BooleanField(default=True)

    events = []

    def update(self):
        self.__clear_previous_events()
        self.__save_events()

    def __clear_previous_events(self):
        """
        Clear saved events where source is current instance.
        """
        ExternalEvent.objects.filter(
            teacher=self.teacher,  # rely upon parent-class created relation
            ext_src_id=ContentType.objects.get_for_model(self).pk,
        ).delete()

    def __save_events(self):
        for ev in self.events:
            ev.save()

    class Meta:
        abstract = True


class GoogleCalendar(ExternalEventSource):
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='google_calendars')

    def poll(self):
        """
        Fetch a calendar, then parse it and populate the `event` property with
        events from it.
        """
        res = self.fetch_calendar(self.url)

        self.events = [event for event in self.parse_events(res)]

    def parse_events(self, ical_str):
        """
        Generator of events parsed from ical_str.

        Repeated events are not supported — you will see only the first one.
        """
        ical = Calendar.from_ical(ical_str)

        for component in ical.walk():
            if component.name == 'VEVENT':
                event = self.parse_event(component)

                if event.start < timezone.now():
                    continue

                yield event

    def parse_event(self, event):
        """
        Return an :model:`extevents.ExternalEvent` instance built from
        an icalendar event.
        """
        (start, end) = self.__event_time(event)
        return ExternalEvent(
            start=start,
            end=end,
            description=event.get('summary'),
            teacher=self.teacher,
            ext_src=self,
        )

    def __event_time(self, event):
        """
        Get a tuple with start and end time of event.

        All timestamps are returned in UTC.
        """
        start = event.get('dtstart').dt
        end = event.get('dtend').dt

        if isinstance(start, datetime.date) and not isinstance(start, datetime.datetime):
            """
            For single-day events we convert datetime.date objects returned
            by icalendar to datetime.datetime objects, adding '00:00' to the start time
            and '23:59' to the end time.
            """
            start = datetime.datetime.combine(start, datetime.time.min.replace(tzinfo=pytz.timezone('UTC')))  # 00:00 in UTC timezone
            end = datetime.datetime.combine(end, datetime.time.min.replace(tzinfo=pytz.timezone('UTC')))  # 23:59 in UTC timezone

        return (start, end)

    def fetch_calendar(self, url):
        r = requests.get(url)
        if r.status_code != 200:
            raise FileNotFoundError('Cannot fetch calendar url (%d)', r.status_code)
        return r.text
