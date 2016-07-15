import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from mixer.backend.django import mixer

from teachers.models import Teacher, WorkingHours


# Create your tests here.

class TestTeachersFunctional(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_superuser('test', 'te@ss.tt', '123')
        self.user.teacher_data = mixer.blend(Teacher, user=self.user)
        self.c.login(username='test', password='123')

    def test_hours_JSON(self):
        mocked_hours = {}

        for i in range(1, 8):
            hours = mixer.blend(WorkingHours, teacher=self.user.teacher_data, weekday=i)
            hours.save()
            mocked_hours[hours.pk] = hours
            print(hours)

        response = self.c.get('/teachers/%s/hours.json' % self.user.username)
        self.assertEquals(response.status_code, 200)

        got_hours = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(got_hours), 7)

        for i in got_hours:
            id = i['id']
            got_mocked_hours = mocked_hours[id]
            self.assertEqual(i['weekday'], got_mocked_hours.weekday)
            self.assertEqual(i['start'], str(got_mocked_hours.start))
            self.assertEqual(i['end'], str(got_mocked_hours.end))
