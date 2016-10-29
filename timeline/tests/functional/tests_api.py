import json
from datetime import timedelta

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from mixer.backend.django import mixer

from elk.utils.testing import ClientTestCase, create_teacher


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

    def test_user(self):  # TODO: REFACTOR IT
        duration = timedelta(minutes=71)

        mocked_entries = {}

        for i in range(0, 10):
            entry = mixer.blend('timeline.Entry', teacher=self.teacher)
            entry.start = entry.start.replace(tzinfo=timezone.get_current_timezone())
            entry.end = entry.start + duration
            entry.save()
            mocked_entries[entry.pk] = entry

        response = self.c.get('/api/timeline/?teacher=%s&start_0=1971-12-01&start_1=2032-11-01' % self.teacher.pk)

        for i in json.loads(response.content.decode('utf-8')):
            id = i['id']
            mocked_entry = mocked_entries[id]

            start = parse_datetime(i['start'])
            end = parse_datetime(i['end'])
            self.assertEqual(start, mocked_entry.start)
            self.assertEqual(end, mocked_entry.end)

    def test_create_user_filter(self):
        x = self.tzdatetime(2016, 1, 1)
        for i in range(0, 10):
            entry = mixer.blend('timeline.Entry', teacher=self.teacher, start=x)
            x += timedelta(days=1)
            entry.save()

        response = self.c.get('/api/timeline/?teacher=%s&?start_0=2013-01-01&start_1=2016-01-03' % self.teacher.pk)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)
