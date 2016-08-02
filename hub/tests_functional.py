import json
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from mixer.backend.django import mixer

import lessons.models as lessons
import products.models as products
from elk.utils.testing import ClientTestCase, create_customer, create_teacher
from hub.exceptions import CannotBeScheduled, CannotBeUnscheduled
from hub.models import Class, Subscription
from teachers.models import WorkingHours
from timeline.models import Entry as TimelineEntry


class BuySubscriptionTestCase(TestCase):
    fixtures = ('crm', 'lessons', 'products')
    TEST_PRODUCT_ID = 1

    def setUp(self):
        self.customer = create_customer()

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
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.save()

        active_lessons_count = Class.objects.filter(subscription_id=s.pk).count()
        active_lessons_in_product_count = _get_lessons_count(product)

        # two lessons with natives and four with curators
        self.assertEqual(active_lessons_count, active_lessons_in_product_count, 'When buying a subscription should add all of its available lessons')

    test_second_time = test_buy_a_single_subscription  # let's test for the second time :-)

    def test_store_class_source(self):
        """
        When buying a subcription, every bought class should have a sign
        about that it's bought buy subscription.
        """

        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150
        )
        s.save()

        for c in s.classes.all():
            self.assertEqual(c.buy_source, 1)  # 1 is defined in the model

    def test_disabling_subscription(self):
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)
        s = Subscription(
            customer=self.customer,
            product=product,
            buy_price=150,
        )
        s.save()

        for lesson in s.classes.all():
            self.assertEqual(lesson.active, 1)

        # now, disable the subscription for any reason
        s.active = 0
        s.save()
        for lesson in s.classes.all():
            self.assertEqual(lesson.active, 0, 'Every lesson in subscription should become inactive now')


class ScheduleTestCase(TestCase):
    fixtures = ('crm', 'lessons')

    def setUp(self):
        self.host = create_teacher()
        self.customer = create_customer()

    def _buy_a_lesson(self, lesson):
        c = Class(
            customer=self.customer,
            lesson=lesson
        )
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
        lesson = products.OrdinaryLesson.get_default()

        entry = mixer.blend(TimelineEntry, slots=1, lesson=lesson)
        bought_class = self._buy_a_lesson(lesson)

        self.assertFalse(bought_class.is_scheduled)
        self.assertTrue(entry.is_free)

        bought_class.assign_entry(entry)  # schedule a class
        bought_class.save()

        self.assertTrue(bought_class.is_scheduled)
        self.assertFalse(entry.is_free)
        self.assertEquals(entry.classes.first().customer, self.customer)

        bought_class.unschedule()
        bought_class.save()
        self.assertFalse(bought_class.is_scheduled)
        self.assertTrue(entry.is_free)

    def test_schedule_auto_entry(self):
        """
        Chedule a class without a timeline entry
        """
        lesson = products.OrdinaryLesson.get_default()
        c = self._buy_a_lesson(lesson)
        c.schedule(
            teacher=self.host,
            date=datetime(2016, 8, 17, 10, 1),
            allow_besides_working_hours=True,
        )
        c.save()

        self.assertIsInstance(c.timeline_entry, TimelineEntry)
        self.assertEquals(c.timeline_entry.classes.first().customer, self.customer)  # should save a customer
        self.assertEquals(c.timeline_entry.start, datetime(2016, 8, 17, 10, 1))  # datetime for entry start should be from parameters
        self.assertEquals(c.timeline_entry.end, datetime(2016, 8, 17, 10, 1) + lesson.duration)  # duration should be taken from lesson

    def test_cant_automatically_schedule_lesson_that_requires_a_timeline_entry(self):
        """
        Scheduling a hosted lesson that requires a timeline entry should fail
        """
        master_class = mixer.blend(lessons.MasterClass, host=self.host)
        c = self._buy_a_lesson(master_class)

        with self.assertRaisesRegexp(CannotBeScheduled, 'timeline entry$'):
            c.schedule(
                teacher=self.host,
                date=datetime(2016, 8, 17, 10, 1)
            )

    def test_schedule_master_class(self):
        """
        Buy a master class and then schedule it
        """
        lesson = mixer.blend(lessons.MasterClass, host=self.host)

        timeline_entry = mixer.blend(TimelineEntry,
                                     lesson=lesson,
                                     teacher=self.host,
                                     )

        timeline_entry.save()

        bought_class = self._buy_a_lesson(lesson=lesson)
        bought_class.save()

        bought_class.assign_entry(timeline_entry)
        bought_class.save()

        self.assertTrue(bought_class.is_scheduled)
        self.assertEqual(timeline_entry.taken_slots, 1)

        bought_class.unschedule()
        self.assertEqual(timeline_entry.taken_slots, 0)

    def test_schedule_2_people_to_a_paired_lesson(self):
        customer1 = create_customer()
        customer2 = create_customer()

        paired_lesson = mixer.blend(lessons.PairedLesson, slots=2)

        customer1_class = Class(
            customer=customer1,
            lesson=paired_lesson
        )
        customer1_class.save()

        customer2_class = Class(
            customer=customer2,
            lesson=paired_lesson
        )
        customer2_class.save()

        timeline_entry = mixer.blend(TimelineEntry, lesson=paired_lesson, teacher=self.host)

        customer1_class.assign_entry(timeline_entry)
        customer1_class.save()

        customer2_class.assign_entry(timeline_entry)
        customer2_class.save()

        self.assertTrue(customer1_class.is_scheduled)
        self.assertTrue(customer2_class.is_scheduled)
        self.assertEqual(timeline_entry.taken_slots, 2)

        customer2_class.unschedule()
        self.assertEqual(timeline_entry.taken_slots, 1)

    def test_schedule_lesson_of_a_wrong_type(self):
        """
        Try to schedule bought master class lesson to a paired lesson event
        """
        paired_lesson = mixer.blend(lessons.PairedLesson, slots=2)
        paired_lesson_entry = mixer.blend(TimelineEntry, lesson=paired_lesson, teacher=self.host, active=1)

        paired_lesson_entry.save()

        bought_class = self._buy_a_lesson(mixer.blend(lessons.MasterClass, host=self.host))
        bought_class.save()

        with self.assertRaises(CannotBeScheduled):
            bought_class.assign_entry(paired_lesson_entry)

        self.assertFalse(bought_class.is_scheduled)


class SchdulingPopupSlotsTestCase(ClientTestCase):
    """
    Simple test suit for testing JSON api, required for scheduling
    popup. Popup queries free slots as lessons (for hosted lessons
    i.e. master classes) and as teachers.
    """
    def setUp(self):
        self.first_teacher = create_teacher()
        mixer.blend(WorkingHours, teacher=self.first_teacher, weekday=0, start='13:00', end='15:30')  # monday
        mixer.blend(WorkingHours, teacher=self.first_teacher, weekday=1, start='17:00', end='19:00')  # thursday

        self.second_teacher = create_teacher()
        mixer.blend(WorkingHours, teacher=self.second_teacher, weekday=0, start='13:00', end='15:00')  # monday
        mixer.blend(WorkingHours, teacher=self.second_teacher, weekday=4, start='17:00', end='19:00')  # thursday

        super().setUp()

    def _buy_a_lesson(self, lesson):
            c = Class(
                customer=self.customer,
                lesson=lesson
            )
            c.save()
            return c

    def test_404(self):
        response = self.c.get('/hub/2032-05-03/type/100500/records.json')
        self.assertEqual(response.status_code, 404)  # non-existent lesson_type

        response = self.c.get('/hub/2032-05-03/type/100500/lessons.json')
        self.assertEqual(response.status_code, 404)  # non-existent lesson_id

        response = self.c.get('/hub/2032-05-03/type/%s/lessons.json' % lessons.MasterClass.get_contenttype().pk)
        self.assertEqual(response.status_code, 404)  # there are no lessons planned

    def test_filter_by_lesson_type(self):
        first_master_class = mixer.blend(lessons.MasterClass, host=self.first_teacher)
        second_master_class = mixer.blend(lessons.MasterClass, host=self.second_teacher)
        entry = TimelineEntry(teacher=self.first_teacher,
                              lesson=first_master_class,
                              start=datetime(2032, 5, 6, 14, 10),
                              end=datetime(2032, 5, 6, 14, 40)
                              )
        entry.save()
        entry = TimelineEntry(teacher=self.second_teacher,
                              lesson=second_master_class,
                              start=datetime(2032, 5, 6, 14, 15),
                              end=datetime(2032, 5, 6, 14, 45)
                              )
        entry.save()
        master_class_type = ContentType.objects.get_for_model(first_master_class)

        response = self.c.get('/hub/2032-05-06/type/%d/lessons.json' % master_class_type.pk)
        self.assertEquals(response.status_code, 200)

        records = json.loads(response.content.decode('utf-8'))
        self.assertEquals(len(records), 2)
        self.assertEquals(len(records[0]['slots']), 1)

        self.assertEquals(records[0]['slots'][0], '14:10')
        self.assertEquals(records[1]['slots'][0], '14:15')

        self.assertEquals(records[0]['name'], first_master_class.name)
        self.assertEquals(records[1]['name'], second_master_class.name)

        self.assertEquals(records[0]['host']['name'], self.first_teacher.user.crm.full_name)
        self.assertEquals(records[1]['host']['name'], self.second_teacher.user.crm.full_name)

    def test_filter_by_date(self):
        response = self.c.get('/hub/2032-05-03/type/%d/teachers.json' % lessons.OrdinaryLesson.get_contenttype().pk)
        self.assertEquals(response.status_code, 200)

        records = json.loads(response.content.decode('utf-8'))

        self.assertEquals(len(records), 2)
        self.assertEquals(len(records[0]['slots']), 5)  # this first teacher works till 15:30
        self.assertEquals(len(records[1]['slots']), 4)  # and the second works till 15:00

        self.assertEquals(records[0]['slots'][-1], '15:00')
        self.assertEquals(records[1]['slots'][-1], '14:30')

        self.assertEquals(records[0]['name'], self.first_teacher.user.crm.full_name)
        self.assertEquals(records[1]['name'], self.second_teacher.user.crm.full_name)

        self.assertNotIn('host', records[0].keys())
        self.assertNotIn('host', records[1].keys())  # records here represent teachers, so don't need any host information
