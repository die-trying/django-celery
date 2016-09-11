import datetime

import pytz
import requests
from django.db import models
from django.utils import timezone
from icalendar import Calendar


class ExternalEvent():
    def __init__(self, start, end, description):
        self.start = start
        self.end = end
        self.description = description


class ExternalEventSource(models.Model):
    url = models.URLField()
    active = models.BooleanField(default=True)

    events = []

    class Meta:
        abstract = True


class GoogleCalendar(ExternalEventSource):
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='google_calendars')

    def poll(self):
        res = self.fetch_calendar(self.url)
        ical = Calendar.from_ical(res)
        self.parse_calendar(ical)

    def parse_calendar(self, ical):
        ical = Calendar.from_ical(ical)

        for component in ical.walk():
            if component.name == 'VEVENT':
                (start, end) = self.__event_time(component)

                if start < timezone.now():
                    next

                self.events.append(ExternalEvent(
                    start=start,
                    end=end,
                    description=component.get('summary'),
                ))

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
