from unittest.mock import patch

from mixer.backend.django import mixer

from crm.models import Customer
from elk.utils.testing import TestCase, create_customer
from products.models import Product1


class TestGreetingTuple(TestCase):
    def test_good_greeting(self):
        self.assertEqual(Customer._greeting('trial'), 'trial')

    def test_bad_greeting(self):
        with self.assertRaises(ValueError):
            Customer._greeting('nonexistant greeting')


class TestGreetingType(TestCase):
    fixtures = ('lessons', 'products')

    def setUp(self):
        self.customer = create_customer()
        self.trial_lesson = mixer.blend('lessons.TrialLesson')
        self.ordinary_lesson = mixer.blend('lessons.OrdinaryLesson')

    def test_greeting_empty(self):
        self.assertEqual(self.customer.get_greeting_type(), 'empty')

    def test_greeting_trial_not_scheduled(self):
        self.customer.classes.create(
            lesson_type=self.trial_lesson.get_contenttype(),
        )
        self.assertEqual(self.customer.get_greeting_type(), 'trial')

    @patch('crm.models.Customer.trial_lesson_is_scheduled')
    def test_greeting_trial_scheduled(self, trial_lesson_is_scheduled):
        trial_lesson_is_scheduled.return_value = True

        self.customer.classes.create(
            lesson_type=self.trial_lesson.get_contenttype(),
        )
        self.assertEqual(self.customer.get_greeting_type(), 'trial-scheduled')

    def test_greeting_trial_used(self):
        self.customer.classes.create(
            lesson_type=self.trial_lesson.get_contenttype(),
        )
        self.customer.classes.update(is_fully_used=True)

        self.assertEqual(self.customer.get_greeting_type(), 'out-of-classes')

    def test_subscription(self):
        self.customer.subscriptions.create(
            product=Product1.objects.get(pk=1),
        )
        self.assertEqual(self.customer.get_greeting_type(), 'subscription-active')

    def test_subscription_finished(self):
        self.customer.subscriptions.create(
            product=Product1.objects.get(pk=1),
            is_fully_used=True,
        )
        self.assertEqual(self.customer.get_greeting_type(), 'subscription-finished')

    def test_no_subscription(self):
        self.customer.classes.create(
            lesson_type=self.ordinary_lesson.get_contenttype(),
        )
        self.assertEqual(self.customer.get_greeting_type(), 'no-subscription')

    def test_purchased_subscription_without_finishing_trial(self):
        """
        Assign a trial lesson and buy a subscription without finising it.
        """
        self.customer.classes.create(
            lesson_type=self.trial_lesson.get_contenttype(),
        )
        self.customer.subscriptions.create(
            product=Product1.objects.get(pk=1),
        )
        self.assertEqual(self.customer.get_greeting_type(), 'subscription-active')

    @patch('crm.models.Customer.can_schedule_classes')
    def test_with_finished_subscription(self, can_schedule_classes):
        can_schedule_classes.return_value = False

        self.customer.subscriptions.create(
            product=Product1.objects.get(pk=1),
        )

        self.assertEqual(self.customer.get_greeting_type(), 'out-of-classes')
