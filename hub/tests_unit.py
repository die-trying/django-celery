from django.test import TestCase
from mixer.backend.django import mixer

import lessons.models as lessons
import products.models as products
from elk.utils.test import mock_request, test_customer, test_teacher
from hub.models import Class, Subscription
from timeline.models import Entry as TimelineEntry


class testBuyableProduct(TestCase):
    fixtures = ('crm', 'lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = test_customer()

    def test_subscription_name(self):
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.request = mock_request(self.customer)
        s.save()

        self.assertEqual(s.name_for_user, product.name)

    def test_single_class_name(self):
        lesson = products.OrdinaryLesson.get_default()
        c = Class(
            customer=self.customer,
            lesson=lesson
        )
        c.request = mock_request(self.customer)
        c.save()

        self.assertEqual(c.name_for_user, lesson.name)


class TestAvailableLessons(TestCase):
    fixtures = ('crm', 'lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = test_customer()
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.request = mock_request()
        s.save()

    def test_available_lesson_types(self):
        lesson_types = self.customer.classes.bought_lesson_types()
        self.assertEquals(len(lesson_types), 5)

        self.assertIn(lessons.OrdinaryLesson.contenttype(), lesson_types)


class TryToSchedule(TestCase):
    fixtures = ('lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = test_customer()
        self.host = test_teacher()

    def _buy_a_lesson(self, lesson):
        c = Class(
            customer=self.customer,
            lesson=lesson
        )
        c.request = mock_request(self.customer)
        c.save()
        return c

    def _buy_a_subscription(self):
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.request = mock_request(self.customer)
        s.save()
        return s

    def test_find_class(self):
        res = Class.objects.find_class(
            customer=self.customer,
            lesson_type=lessons.OrdinaryLesson.contenttype()
        )
        self.assertFalse(res['result'])
        self.assertEquals(res['error'], 'E_CLASS_NOT_FOUND')
        self.assertIn('curated session', res['text'])  # err text should contain name of the lesson

        self._buy_a_lesson(lessons.OrdinaryLesson.get_default())
        res = Class.objects.find_class(
            customer=self.customer,
            lesson_type=lessons.OrdinaryLesson.contenttype()
        )
        self.assertTrue(res['result'])  # should find now
        self.assertIsInstance(res['class'], Class)

    def test_find_only_active_classes(self):
        lesson = lessons.OrdinaryLesson.get_default()
        entry = mixer.blend(TimelineEntry, lesson=lesson, teacher=self.host, active=1)
        c = self._buy_a_lesson(lesson)

        c.schedule(entry)
        c.save()

        res = Class.objects.find_class(
            customer=self.customer,
            lesson_type=lessons.OrdinaryLesson.contenttype()
        )
        self.assertFalse(res['result'])  # we already have scheduled the only class we could

    def test_find_the_subscription_class_first(self):
        """
        Return subscription lessons first.

        Buy a single lesson, than buy a subscription an check, that find_class()
        would return a subscription lesson.
        """
        self._buy_a_lesson(lessons.OrdinaryLesson.get_default())
        subscription = self._buy_a_subscription()

        first_lesson_by_subscription = Class.objects.order_by('buy_date', 'id').filter(subscription=subscription)[0]

        res = Class.objects.find_class(
            customer=self.customer,
            lesson_type=lessons.OrdinaryLesson.contenttype()
        )
        self.assertTrue(res['result'])
        self.assertEquals(res['class'], first_lesson_by_subscription)
