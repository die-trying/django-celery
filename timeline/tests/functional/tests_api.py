import json
from datetime import timedelta

from django.utils import timezone
from django.utils.dateformat import format
from django.utils.dateparse import parse_datetime
from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import APITestCase, create_customer, create_teacher
from lessons import models as lessons


class EntryAPITest(APITestCase):
    """
    Generate dummy teachers timeline and fetch it through JSON
    """
    def setUp(self):
        """
        Calendar administration is limited to staff members, so we login
        with a super user here.
        """
        self.teacher = create_teacher()
        self.c.login(username=self.superuser_login, password=self.superuser_password)

    def tearDown(self):
        super().tearDown()
        self.c.logout()

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

        response = self.c.get('/api/timeline/', {
            'teacher': self.teacher.pk,
            'start_0': '2013-01-01',
            'start_1': '2016-01-03',
        })
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 3)

    def test_api_permissions(self):
        someone = create_customer(password='123')

        self.c.logout()
        self.c.login(username=someone.user.username, password='123')
        response = self.c.get('/api/timeline/')

        self.assertEqual(response.status_code, 403)


@freeze_time('2032-12-01 12:00')
class EntryScheduleCheckAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = create_teacher()
        cls.lesson = mixer.blend(lessons.MasterClass, host=cls.teacher, slots=5)
        cls.entry = mixer.blend(
            'timeline.Entry',
            teacher=cls.teacher,
            lesson=cls.lesson,
            start=cls.tzdatetime(2032, 12, 5, 12, 0)
        )

    def test_non_staff_can_access_the_endpoint(self):
        someone = create_customer(password='123')

        self.c.logout()
        self.c.login(username=someone.user.username, password='123')
        response = self.c.get('/api/timeline/%d/schedule_check/' % self.entry.pk)

        self.assertEqual(response.status_code, 200)

    def test_find_entry(self):
        search_url = '/timeline/find_entry/{teacher}/{lesson_type}/{lesson_id}/{start}/'.format(
            teacher=self.teacher.user.username,
            lesson_type=self.lesson.get_contenttype().pk,
            lesson_id=self.lesson.pk,
            start=format(self.entry.start, 'c')
        )

        response = self.c.get(search_url)

        self.assertRedirectsPartial(response, '%d/schedule_check' % self.entry.pk)  # should redirect to the schedule_check url
