from mixer.backend.django import mixer

import lessons.models as lessons
from elk.utils.testing import ClientTestCase, create_customer, create_teacher, mock_request
from hub.models import Class

from . import views


class SchedulingPopupTestCaseBase(ClientTestCase):
    fixtures = ('lessons',)

    def setUp(self):
        self.customer = create_customer()
        self.host = create_teacher()
        super().setUp()

    def _buy_a_lesson(self, lesson):
        c = Class(
            customer=self.customer,
            lesson=lesson
        )
        c.request = mock_request(self.customer)
        c.save()
        return c

    def _get_step1(self):
        request = self.factory.get('/hub/schedule/step1/')
        request.user = self.customer.user
        return views.step1(request)


class TestSchedulingPopupHTML(SchedulingPopupTestCaseBase):

    def test_lesson_categories(self):
        """
        Buy two lessons of different type and assure that filter of two types
        has appeared in the scheduling popup.
        """
        self._buy_a_lesson(lessons.OrdinaryLesson.get_default())
        self._buy_a_lesson(mixer.blend(lessons.MasterClass, host=self.host))
        self.assertEquals(self.customer.classes.count(), 2)

        response = self._get_step1()
        with self.assertHTML(response, '.schedule-popup__filters .lesson_type label') as categories:
            self.assertEquals(len(categories), 2)  # user has only two lessons bought — Ordinary lesson and a Master class
            for category in categories:
                self.assertIn(int(category.find('input').attrib.get('value')), [lessons.OrdinaryLesson.contenttype().pk, lessons.MasterClass.contenttype().pk])  # every value of checkbox should be an allowed contenttype
                self.assertNotEqual(len(category.text_content()), 0)  # every lesson type should have a NAME, like <label><input type=radio value="1">NAME</label>.

    def test_popup_without_bought_lessons(self):
        """
        Request a scheduling popup for user without bought classes.
        """
        response = self._get_step1()
        self.assertEquals(response.status_code, 200)  # should not throw anything

    def test_date_selector(self):
        """
        Test date filter — it should exist and have 7 days to select
        """
        self._buy_a_lesson(lessons.OrdinaryLesson.get_default())
        response = self._get_step1()
        with self.assertHTML(response, '.schedule-popup__date-selector select') as (date_selector,):
            options = [i for i in date_selector.findall('option')]
            self.assertEquals(len(options), 7)  # popup has 7 days forward to select


class TestSchedulingPopupAPI(SchedulingPopupTestCaseBase):
    """
    Test server-side checking of available lessons
    """
    pass
