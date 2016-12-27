from freezegun import freeze_time

from elk.utils.testing import ClientTestCase, create_customer, create_teacher
from teachers.slot_list import SlotList


@freeze_time('2001-01-01 12:00')
class TestTeacherViews(ClientTestCase):
    def setUp(self):
        self.teacher = create_teacher(works_24x7=True)
        self.other_teachers = [create_teacher() for i in range(1, 10)]

    def test_list_loading(self):
        """
        Test teacher list

        Feel free to modify assertions when you change teacher sort order
        """
        response = self.c.get('/teachers/')

        with self.assertHTML(response, '.teacher-grid a') as teacher_link:
            self.assertEqual(len(teacher_link), 10)

    def test_detail_loading(self):
        response = self.c.get('/teachers/%s/' % self.teacher.user.username)

        with self.assertHTML(response, 'img.teacher-face') as teacher_face:
            self.assertIsNotNone(teacher_face)

    def test_no_teacher_detail_for_non_teacher_user(self):
        some_random_man = create_customer()
        response = self.c.get('/teachers/%s/' % some_random_man.user.username)

        self.assertEqual(response.status_code, 404)

    def test_teacher_detail_slots_list(self):
        response = self.c.get('/teachers/%s/' % self.teacher.user.username)
        self.assertGreaterEqual(len(response.context['timeslots']), 7)

        first_day = response.context['timeslots'][0]
        self.assertIsInstance(first_day['slots'], SlotList)
        print(first_day['slots'])
        self.assertGreaterEqual(len(first_day['slots']), 10)
