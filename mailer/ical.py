from datetime import timedelta
from urllib.parse import urlparse

import icalendar
from django.conf import settings


class Ical():
    def __init__(self, start, end, summary, uid, method='request'):
        self.start = start
        self.end = end
        self.summary = summary
        self.uid = uid
        self.method = method

        self.calendar = self._build_calendar()

    def _build_calendar(self):
        calendar = self._calendar_boilerplate()
        calendar.add_component(self._event())
        calendar.add_component(self.__alarm())

        return calendar

    def as_string(self):
        return self.calendar.to_ical().decode('utf-8')

    def _calendar_boilerplate(self):
        calendar = icalendar.Calendar()
        calendar.add('method', self.method.upper())  # method can be e.g. 'cancel'
        calendar.add('version', '2.0')
        calendar.add('prodid', '-//ELK/Dashboard')

        return calendar

    def _event(self):
        event = self._event_boilerplate()
        event.add('dtstart', self.start)
        event.add('dtstamp', self.start)
        event.add('dtend', self.end)
        event.add('summary', self.summary)

        return event

    def _event_boilerplate(self):
        event = icalendar.Event()
        event.add('sequence', 0)  # should increase it when updating event

        event.add('uid', self.__uid())
        event.add('ogranizer', self.__organizer(), encode=0)

        return event

    def __uid(self):
        return '{uid}@{host}'.format(
            uid=self.uid,
            host=urlparse(settings.ABSOLUTE_HOST).netloc,
        )

    def __organizer(self):
        return icalendar.vCalAddress('MAILTO:%s' % settings.SUPPORT_EMAIL)

    def __alarm(self):
        alarm = icalendar.Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('trigger', timedelta(minutes=-30))

        return alarm
