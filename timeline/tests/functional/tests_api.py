import json
from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from mixer.backend.django import mixer

from elk.utils.testing import ClientTestCase, create_teacher
from timeline.models import Entry as TimelineEntry


class EntryAPITest(ClientTestCase):
    """
    Generate dummy teachers timeline and fetch it through JSON
    """
    def setUp(self):
        """
        Calendar administration is limited to staff members, so we login
        with a super user here.
        """
        self.teacher = create_teacher()

        super().setUp()

    def test_user(self):  # TODO: REFACTOR IT
        duration = timedelta(minutes=71)

        mocked_entries = {}

        for i in range(0, 10):
            entry = mixer.blend(TimelineEntry,
                                teacher=self.teacher,
                                # start=(now),
                                # end=(now + duration),
                                )
            entry.start = entry.start.replace(tzinfo=timezone.get_current_timezone())
            entry.end = entry.start + duration
            entry.save()
            mocked_entries[entry.pk] = entry

        response = self.c.get('/timeline/%s.json?start=1971-12-01&end=2032-11-01' % self.teacher.user.username)

        for i in json.loads(response.content.decode('utf-8')):
            id = i['id']
            mocked_entry = mocked_entries[id]

            start = parse_datetime(i['start'])
            end = parse_datetime(i['end'])
            self.assertEqual(start, mocked_entry.start)
            self.assertEqual(end, mocked_entry.end)

    def test_create_user_filter(self):
        x = parse_date('2016-01-01')
        for i in range(0, 10):
            entry = mixer.blend(TimelineEntry, teacher=self.teacher, start=x)
            x += timedelta(days=1)
            print(x.__class__)
            entry.save()

        response = self.c.get('/timeline/%s.json?start=2013-01-01&end=2016-01-03' % self.teacher.user.username)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)
