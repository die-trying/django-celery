from unittest.mock import MagicMock

from django.http import Http404
from mixer.backend.django import mixer

from elk.utils.testing import ClientTestCase, create_customer, create_teacher
from lessons import models as lessons
from market import views
from market.models import Class


class UserCancellationTestCase(ClientTestCase):
    def setUp(self):
        self.customer = create_customer()
        self.teacher = create_teacher(works_24x7=True)
        self.lesson = mixer.blend(lessons.OrdinaryLesson, customer=self.customer)

    def _buy_a_lesson(self):
        c = Class(
            customer=self.customer,
            lesson_type=self.lesson.get_contenttype()
        )
        c.save()
        return c

    def _schedule(self, c, date=None):
        if date is None:
            date = self.tzdatetime(2032, 12, 1, 11, 30)
        c.schedule(
            teacher=self.teacher,
            date=date,
            allow_besides_working_hours=True,
        )
        c.save()
        self.assertTrue(c.is_scheduled)
        return c

    def test_cancellation_popup(self):
        c = self._buy_a_lesson()
        self._schedule(c)

        request = self.factory.get('/market/cancel/11/popup')
        request.user = self.customer.user
        response = views.cancel_popup(request, c.pk)
        with self.assertHTML(response, "button[data-class-cancellation-url]") as (submit,):
            self.assertEqual(submit.attrib.get('data-class-cancellation-url'), '/market/cancel/%d/' % c.pk)

    def test_sorry_popup(self):
        """
        Request cancellation with a customer, that can't do thant
        """
        c = self._buy_a_lesson()
        self._schedule(c)
        self.customer.can_cancel_classes = MagicMock(return_value=False)
        request = self.factory.get('/market/cancel/11/popup')
        request.user = self.customer.user
        response = views.cancel_popup(request, c.pk)
        with self.assertHTML(response, "h3.modal-title") as (popup_title,):
            self.assertIn('Sorry', popup_title.text_content())

    def test_404_for_non_scheduled_class(self):
        c = self._buy_a_lesson()
        request = self.factory.get('/market/cancel/11/popup')
        request.user = self.customer.user
        with self.assertRaises(Http404):
            views.cancel_popup(request, c.pk)

    def test_404_for_others_classes(self):
        c = self._buy_a_lesson()
        self._schedule(c)

        request = self.factory.get('/market/cancel/11/popup')

        other_customer = create_customer()
        request.user = other_customer.user

        with self.assertRaises(Http404):
            views.cancel_popup(request, c.pk)

        with self.assertRaises(Http404):
            views.cancel(request, c.pk)

    def test_actual_cancellation(self):
        c = self._buy_a_lesson()
        self._schedule(c)

        c.refresh_from_db()
        self.assertTrue(c.is_scheduled)

        request = self.factory.get('/market/cancel/111')
        request.user = self.customer.user

        response = views.cancel(request, c.pk)
        self.assertEqual(response.status_code, 200)

        c.refresh_from_db()
        self.assertFalse(c.is_scheduled)
