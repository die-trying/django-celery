import json

from mixer.backend.django import mixer

from elk.utils.testing import ClientTestCase, create_teacher
from teachers.models import WorkingHours


class TestWorkingHours(ClientTestCase):
    def setUp(self):
        self.teacher = create_teacher()
        mixer.blend(WorkingHours, teacher=self.teacher, weekday=0, start='13:00', end='15:00')  # monday
        mixer.blend(WorkingHours, teacher=self.teacher, weekday=1, start='17:00', end='19:00')  # thursday

    def test_hours_json(self):
        """
        Test for generated json with teacher's working hours.
        """
        response = self.c.get('/teachers/%s/hours.json' % self.teacher.user.username)
        self.assertEquals(response.status_code, 200)

        got_hours = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(got_hours), 2)

        hours = got_hours[0]
        self.assertEqual(hours['weekday'], 0)
        self.assertIn('13:00', hours['start'])
        self.assertIn('15:00', hours['end'])
