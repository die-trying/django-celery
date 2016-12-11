import csv

from freezegun import freeze_time
from mixer.backend.django import mixer

from elk.utils.testing import ClassIntegrationTestCase, create_customer
from timeline.models import Entry as TimelineEntry


@freeze_time('2032-01-01 15:00')
class TestExportLastLessons(ClassIntegrationTestCase):
    def test_single_customer(self):
        """
        1. Buy a lesson for customer, schedule it
        2. Mark it as finished
        3. Check completed_lesson report for this customer
        """
        c = self._buy_a_lesson()
        entry = self._create_entry()
        entry = self._schedule(c, entry)

        TimelineEntry.objects.filter(classes__customer=self.customer).update(is_finished=True)  # mark as finished

        response = self.c.get('/crm/export_last_lessons/%s/start/2016-01-12/end/2033-01-01/' % self.customer.pk)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8').strip().split('\n')
        got = list(csv.reader(content, delimiter="\t"))

        self.assertEqual(len(got), 2)

        completed_class = got[1]
        self.assertIsNotNone(completed_class[0])
        self.assertEqual(completed_class[1], str(self.customer))
        self.assertEqual(completed_class[2], self.host.user.crm.full_name)
        self.assertIsNotNone(completed_class[3])

    def test_multiple_customers(self):
        """
        1. Buy a lesson for customer, schedule it
        2. Buy the same lesson for another customer
        3. Mark lesson is finished
        4. Check completed_lesson report for this customer
            * Should contain two customers
            * Should contain only one record because two customers were on the same lesson
        """
        self.lesson = mixer.blend('lessons.MasterClass', host=self.host, slots=5)

        c = self._buy_a_lesson()
        entry = self._create_entry()
        entry.slots = 5
        entry.save()

        self._schedule(c, entry)

        first_customer = self.customer
        second_customer = self.customer = create_customer()

        c1 = self._buy_a_lesson()
        self._schedule(c1, entry)

        TimelineEntry.objects.filter(classes__customer=self.customer).update(is_finished=True)  # mark as finished

        response = self.c.get('/crm/export_last_lessons/%s/start/2016-01-12/end/2033-01-01/' % ','.join([str(first_customer.pk), str(second_customer.pk)]))
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8').strip().split('\n')
        got = list(csv.reader(content, delimiter="\t"))

        self.assertEqual(len(got), 2)  # 3 here meens that two customers that were on a a single lesson are shown in one row

        completed_class = got[1]
        self.assertIsNotNone(completed_class[0])
        self.assertIn(str(first_customer), completed_class[1])
        self.assertIn(str(second_customer), completed_class[1])
        self.assertEqual(completed_class[2], self.host.user.crm.full_name)
        self.assertIsNotNone(completed_class[3])

    def test_staff_only(self):
        someone = create_customer(password='jahvae1Zoozu')
        self.c.logout()
        self.c.login(username=someone.user.username, password='jahvae1Zoozu')

        response = self.c.get('/crm/export_last_lessons/%s/start/2016-01-12/end/2033-01-01/' % self.customer.pk)
        self.assertRedirectsPartial(response, '/accounts/login')
