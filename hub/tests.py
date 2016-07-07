from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from mixer.backend.django import mixer

import lessons.models as lessons
import products.models as products
from crm.models import Customer
from elk.utils.mockers import mock_request
from elk.utils.reflection import find_ancestors
from hub.exceptions import CannotBeScheduled, CannotBeUnscheduled
from hub.models import ActiveSubscription, Class
from timeline.models import Entry as TimelineEntry


class BuySubscriptionTestCase(TestCase):
    fixtures = ('crm', 'lessons', 'products')
    TEST_PRODUCT_ID = 1

    def test_buy_a_single_subscription(self):
        """
        When buing a subscription, all lessons in it should become beeing
        available to the customer
        """

        # TODO: Clean this up
        def _get_lessons_count(product):
            cnt = 0
            for lesson_type in product.LESSONS:
                cnt += getattr(product, lesson_type).all().count()
            return cnt

        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        customer = mixer.blend(Customer)
        s = ActiveSubscription(
            customer=customer,
            product=product,
            buy_price=150,
        )
        s.request = mock_request(customer)
        s.save()

        active_lessons_count = Class.objects.filter(subscription_id=s.pk).count()
        active_lessons_in_product_count = _get_lessons_count(product)

        self.assertEqual(active_lessons_count, active_lessons_in_product_count, 'When buying a subscription should add all of its available lessons')  # two lessons with natives and four with curators

    test_second_time = test_buy_a_single_subscription  # let's test for the second time :-)

    def test_store_class_source(self):
        """
        When buying a subcription, every bought class should have a sign
        about that it's bought buy subscription.
        """

        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        customer = mixer.blend(Customer)
        s = ActiveSubscription(
            customer=customer,
            product=product,
            buy_price=150
        )
        s.request = mock_request(customer)
        s.save()

        for c in s.classes.all():
            self.assertEqual(c.buy_source, 1)  # 1 is defined in the model

    def test_disabling_subscription(self):
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        customer = mixer.blend(Customer)
        s = ActiveSubscription(
            customer=customer,
            product=product,
            buy_price=150,
        )
        s.request = mock_request(customer)
        s.save()

        for lesson in s.classes.all():
            self.assertEqual(lesson.active, 1)

        # now, disable the subscription for any reason
        s.active = 0
        s.save()
        for lesson in s.classes.all():
            self.assertEqual(lesson.active, 0, 'Every lesson in subscription should become inactive now')


class BuySingleLessonTestCase(TestCase):
    fixtures = ('crm', 'lessons', 'products')

    def test_single_lesson(self):
        """
        Let's but ten lessons at a time
        """
        customer = mixer.blend(Customer)
        for lesson_type in find_ancestors(lessons, lessons.Lesson):
            already_bought_lessons = []
            for i in range(0, 10):
                try:
                    c = Class(
                        customer=customer,
                        lesson=lesson_type.get_default()  # this should be defined in every lesson
                    )
                    c.request = mock_request(customer)
                    c.save()
                    self.assertTrue(c.pk)
                    self.assertNotIn(c.pk, already_bought_lessons)
                    already_bought_lessons.append(c.pk)
                except NotImplementedError:
                    """
                    Some lessons, ex master classes cannot be bought such way
                    """
                    pass


class ScheduleTestCase(TestCase):
    fixtures = ('crm', 'lessons')
    TEST_CUSTOMER_ID = 1

    def setUp(self):
        self.event_host = mixer.blend(User, is_staff=1)

    def _buy_a_lesson(self, lesson):
        customer = Customer.objects.get(pk=self.TEST_CUSTOMER_ID)
        c = Class(
            customer=customer,
            lesson=lesson
        )
        c.request = mock_request(customer)
        c.save()
        return c

    def test_unschedule_of_non_scheduled_lesson(self):
        bought_class = self._buy_a_lesson(products.OrdinaryLesson.get_default())
        with self.assertRaises(CannotBeUnscheduled):
            bought_class.unschedule()

    def test_schedule_simple(self):
        """
        Generic test to schedule and unschedule a class
        """

        entry = mixer.blend(TimelineEntry, slots=1)
        bought_class = self._buy_a_lesson(products.OrdinaryLesson.get_default())

        self.assertFalse(bought_class.is_scheduled)
        self.assertTrue(entry.is_free)

        bought_class.schedule(entry)  # schedule a class
        bought_class.save()

        self.assertTrue(bought_class.is_scheduled)
        self.assertFalse(entry.is_free)

        bought_class.unschedule()
        self.assertFalse(bought_class.is_scheduled)
        self.assertTrue(entry.is_free)

    def test_schedule_master_class(self):
        """
        Buy a master class and then schedule it
        """
        event = mixer.blend(lessons.Event,
                            lesson_type=ContentType.objects.get(app_label='lessons', model='masterclass'),
                            slots=5,
                            host=self.event_host,
                            )

        lesson = mixer.blend(lessons.MasterClass)

        timeline_entry = mixer.blend(TimelineEntry,
                                     event=event,
                                     teacher=self.event_host,
                                     )

        timeline_entry.save()

        bought_class = self._buy_a_lesson(lesson=lesson)
        bought_class.save()

        bought_class.schedule(timeline_entry)
        bought_class.save()

        self.assertTrue(bought_class.is_scheduled)
        self.assertEqual(timeline_entry.taken_slots, 1)

        bought_class.unschedule()
        self.assertEqual(timeline_entry.taken_slots, 0)

    def schedule_2_people_to_a_paired_lesson(self):
        event = mixer.blend(lessons.Event,
                            lesson_type=ContentType.objects.get(app_label='lessons', model='pairedlesson'),
                            slots=2,
                            host=self.event_host,
                            )
        customer1 = mixer.blend(Customer)
        customer2 = mixer.blend(Customer)

        paired_lesson = mixer.blend(lessons.PairedLesson, slots=2)

        customer1_class = mixer.blend(Class, customer=customer1, lesson=paired_lesson)
        customer2_class = mixer.blend(Class, customer=customer2, lesson=paired_lesson)

        timeline_entry = mixer.blend(TimelineEntry, event=event, teacher=self.event_host)

        customer1_class.schedule(timeline_entry)
        customer2_class.schedule(timeline_entry)

        self.assertTrue(customer1_class.is_scheduled)
        self.assertTrue(customer2_class.is_scheduled)
        self.assertEqual(timeline_entry.taken_slots, 2)

        customer2_class.unschedule()
        self.assertEqual(timeline_entry.taken_slots, 1)

    def test_schedule_lesson_of_a_wrong_type(self):
        """
        Try to schedule bought master class lesson to a paired lesson event
        """
        event = mixer.blend(lessons.Event,
                            lesson_type=ContentType.objects.get(app_label='lessons', model='pairedlesson'),
                            slots=2,
                            host=self.event_host,
                            )

        paired_lesson_entry = mixer.blend(TimelineEntry, event=event, teacher=self.event_host)

        paired_lesson_entry.save()

        bought_class = self._buy_a_lesson(mixer.blend(lessons.MasterClass))
        bought_class.save()

        with self.assertRaises(CannotBeScheduled):
            bought_class.schedule(paired_lesson_entry)

        self.assertFalse(bought_class.is_scheduled)


class testBuyableProductMixin(TestCase):
    fixtures = ('crm', 'lessons', 'products')
    TEST_PRODUCT_ID = 1

    def test_subscription_name(self):
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        customer = mixer.blend(Customer)
        s = ActiveSubscription(
            customer=customer,
            product=product,
            buy_price=150,
        )
        s.request = mock_request(customer)
        s.save()

        self.assertEqual(s.name_for_user, product.name)

    def test_single_class_name(self):
        customer = mixer.blend(Customer)
        lesson = products.OrdinaryLesson.get_default()
        c = Class(
            customer=customer,
            lesson=lesson
        )
        c.request = mock_request(customer)
        c.save()

        self.assertEqual(c.name_for_user, lesson.name)
