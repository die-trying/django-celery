from django.test import TestCase

from elk.utils.reflection import find_ancestors

from crm.models import Customer
from hub.models import ActiveSubscription, Class
from timeline.models import Entry as TimelineEntry

import products.models as products
import lessons.models as lessons


class BuySubscriptionTestCase(TestCase):
    fixtures = ('crm', 'lessons', 'products')
    TEST_PRODUCT_ID = 1
    TEST_CUSTOMER_ID = 1

    def testBuySingleSubscription(self):
        """
        When buing a subscription, all lessons in it should become beeing
        available to the customer
        """

        def _get_lessons_count(product):
            cnt = 0
            for lesson_type in product.LESSONS:
                cnt += getattr(product, lesson_type).all().count()
            return cnt

        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)

        s = ActiveSubscription(
            customer=Customer.objects.get(pk=self.TEST_CUSTOMER_ID),
            product=product,
            buy_price=150,
        )
        s.save()

        active_lessons_count = Class.objects.filter(subscription_id=s.pk).count()
        active_lessons_in_product_count = _get_lessons_count(product)

        self.assertEqual(active_lessons_count, active_lessons_in_product_count, 'When buying a subscription should add all of its available lessons')  # two lessons with natives and four with curators

    testBuySingleSubscriptionSecondTime = testBuySingleSubscription  # let's test for the second time :-)

    def testDisablingSubscription(self):
        product = products.Product1.objects.get(pk=self.TEST_PRODUCT_ID)

        s = ActiveSubscription(
            customer=Customer.objects.get(pk=self.TEST_CUSTOMER_ID),
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


class BuySingleLessonTestCase(TestCase):
    fixtures = ('crm', 'lessons', 'products')

    TEST_CUSTOMER_ID = 1

    def testSingleLesson(self):
        """
        Let's but ten lessons at a time
        """
        for lesson_type in find_ancestors(lessons, lessons.Lesson):
            already_bought_lessons = []
            for i in range(0, 10):
                try:
                    s = Class(
                        customer=Customer.objects.get(pk=self.TEST_CUSTOMER_ID),
                        lesson=lesson_type.get_default()  # this should be defined in every lesson
                    )
                    s.save()
                    self.assertTrue(s.pk)
                    self.assertNotIn(s.pk, already_bought_lessons)
                    already_bought_lessons.append(s.pk)
                except NotImplementedError:
                    """
                    Some lessons, ex master classes cannot be bought such way
                    """
                    pass


class ScheduleTestCase(TestCase):
    fixtures = ('crm.yaml', 'test_timeline_entries.yaml')
    TEST_CUSTOMER_ID = 1

    def _buy_a_lesson(self, lesson=products.OrdinaryLesson.get_default()):
        bought_class = Class(
            customer=Customer.objects.get(pk=self.TEST_CUSTOMER_ID),
            lesson=lesson
        )
        bought_class.save()
        return bought_class

    def testScheduleSimple(self):
        """
        Generic test to schedule and unschedule a class

        TODO REWRITE THIS

        Разобраться, почему тест падает. Вероятно, это связано с тем, что я переделал учет свободности
        времени преподавателя на слоты, но забыл добавить обработку слотов для простых уроков, к которым совсем
        не привязаны события
        """
        SIMPLE_ENTRY_ID = 1

        entry = TimelineEntry.objects.get(pk=SIMPLE_ENTRY_ID)
        self.assertTrue(entry.is_free)

        bought_class = self._buy_a_lesson()
        self.assertFalse(bought_class.is_scheduled)

        bought_class.schedule(entry)  # schedule a class

        entry = TimelineEntry.objects.get(pk=SIMPLE_ENTRY_ID)
        self.assertFalse(entry.is_free, 'Entry should be occupied after scheduling')

        self.assertEquals(bought_class.event.pk, SIMPLE_ENTRY_ID)

        self.assertTrue(bought_class.is_scheduled, 'Class should be marked as scheduled now')

        bought_class.unschedule()
        entry = TimelineEntry.objects.get(pk=SIMPLE_ENTRY_ID)
        self.assertTrue(entry.is_free, 'Entry should become free again after scheduling')
        self.assertIsNone(bought_class.event)
