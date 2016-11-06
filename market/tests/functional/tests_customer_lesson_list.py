from django.test import override_settings
from mixer.backend.django import mixer

from elk.utils.testing import ClassIntegrationTestCase, create_customer
from lessons import models as lessons


@override_settings(TIME_ZONE='UTC')
class TestCustomerLessonList(ClassIntegrationTestCase):
    def setUp(self):
        super().setUp()

        self.customer = create_customer(timezone='UTC')  # avoid timezone issues during re-login
        self.customer.user.set_password('hidooZohLu0e')
        self.customer.user.save()

        self.c.logout()
        self.c.login(username=self.customer.user.username, password='hidooZohLu0e')

    def _schedule_a_lesson(self):
        c = self._buy_a_lesson()
        entry = self._create_entry()
        self._schedule(c, entry)

        return c

    def test_no_error_without_lessons(self):
        response = self.c.get('/market/mylessons/')
        self.assertEqual(response.status_code, 200)

    def test_plan_single_lesson(self):
        self.lesson = lessons.OrdinaryLesson.get_default()

        self._schedule_a_lesson()

        response = self.c.get('/market/mylessons/')

        with self.assertHTML(response, '.customer-lessons td') as lesson_param:
            self.assertIn('2032', lesson_param[0].text.strip())
            self.assertEqual(lesson_param[1].text.strip(), 'Curated lesson')
            self.assertEqual(lesson_param[2].text.strip(), self.host.user.crm.full_name)
            self.assertEqual(lesson_param[3].text, '\xa0')  # &nbsp;

    def test_finish_signle_lesson(self):
        self.lesson = lessons.OrdinaryLesson.get_default()

        c = self._schedule_a_lesson()

        c.mark_as_fully_used()

        response = self.c.get('/market/mylessons/')

        with self.assertHTML(response, '.customer-lessons td') as lesson_param:
            self.assertEqual(lesson_param[3].text, 'Yes')

    def test_master_class(self):
        self.lesson = mixer.blend(lessons.MasterClass, host=self.host, slots=5)

        entry = self._create_entry()

        entry.slots = 5
        entry.save()

        print(entry.start)
        c = self._buy_a_lesson()
        self._schedule(c, entry)

        self.customer = create_customer()  # Addding another customer to the same lesson
        c = self._buy_a_lesson()
        self._schedule(c, entry)

        response = self.c.get('/market/mylessons/')

        with self.assertHTML(response, '.customer-lessons td') as lesson_param:
            self.assertIn('2032', lesson_param[0].text.strip())
            self.assertIn('Master class', lesson_param[1].text.strip())
            self.assertEqual(lesson_param[2].text.strip(), self.host.user.crm.full_name)
