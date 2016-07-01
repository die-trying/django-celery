from django.test import TestCase

from .models import Entry as TimelineEntry
from crm.models import Customer


class EntryTestCase(TestCase):
    fixtures = ('crm', 'test_timeline_entries',)

    def _occupy(self, entry):
        entry.customer = Customer.objects.get(pk=1)
        entry.save()

    def _free(self, entry):
        entry.customer = None
        entry.save()

    def testIsOccupied(self):
        """
        Take a free entry, occupy it, and get it back free
        """
        entry = TimelineEntry.objects.get(pk=1)

        self.assertTrue(entry.is_free)

        self._occupy(entry)
        self.assertFalse(entry.is_free)

        self._free(entry)
        self.assertTrue(entry.is_free)

    def testFindFreeEntries(self):
        free_entries = TimelineEntry.objects.all().free()
        cnt = free_entries.count()
        self.assertGreater(cnt, 0)

        entry = free_entries[0]
        self._occupy(entry)

        free_entries = TimelineEntry.objects.all().free()
        self.assertEqual(free_entries.count(), cnt - 1)

        self._free(entry)
        free_entries = TimelineEntry.objects.all().free()
        self.assertEqual(free_entries.count(), cnt)
