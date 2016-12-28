from django.apps import apps
from django.contrib.admin.models import LogEntry

from elk.logging import write_admin_log_entry
from elk.utils.testing import TestCase, create_customer
from lessons import models as lessons


class TestBundledAdminLogging(TestCase):
    fixtures = ['lessons']

    def setUp(self):
        self.customer = create_customer()

    def test_write_admin_log_entry(self):
        Class = apps.get_model('market.Class')
        c = Class(
            customer=self.customer,
            lesson_type=lessons.OrdinaryLesson.get_contenttype()
        )

        user = create_customer().user
        write_admin_log_entry(user, c, msg='Testing')

        log_entry = LogEntry.objects.first()

        self.assertEqual(log_entry.change_message, 'Testing')
        self.assertEqual(log_entry.user, user)
