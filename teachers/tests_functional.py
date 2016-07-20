import json

from mixer.backend.django import mixer

from elk.utils.test import ClientTestCase, test_teacher
from teachers.models import WorkingHours


class TestWorkingHours(ClientTestCase):
    def setUp(self):
        self.teacher = test_teacher()
        super().setUp()

    def test_hours_JSON(self):
        """
        Test for generated json with teacher's working hours.
        """
        mocked_hours = {}

        for i in range(0, 7):
            hours = mixer.blend(WorkingHours, teacher=self.teacher, weekday=i)
            hours.save()
            mocked_hours[hours.pk] = hours
            print(hours)

        response = self.c.get('/teachers/%s/hours.json' % self.teacher.user.username)
        self.assertEquals(response.status_code, 200)

        got_hours = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(got_hours), 7)

        for i in got_hours:
            id = i['id']
            got_mocked_hours = mocked_hours[id]
            self.assertEqual(i['weekday'], got_mocked_hours.weekday)
            self.assertEqual(i['start'], str(got_mocked_hours.start))
            self.assertEqual(i['end'], str(got_mocked_hours.end))
