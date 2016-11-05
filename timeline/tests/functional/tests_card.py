from datetime import timedelta

from django.core.urlresolvers import reverse
from mixer.backend.django import mixer

from elk.utils.testing import ClientTestCase, create_customer, create_teacher
from lessons import models as lessons
from market.models import Class
from timeline.models import Entry as TimelineEntry


class EntryCardTest(ClientTestCase):
    def setUp(self):
        self.teacher = create_teacher(works_24x7=True)
        self.customer = create_customer()
        self.lesson = mixer.blend(lessons.MasterClass, host=self.teacher, duration=timedelta(minutes=33), slots=8)

        self.entry = mixer.blend(TimelineEntry,
                                 teacher=self.teacher,
                                 lesson=self.lesson,
                                 start=self.tzdatetime(2032, 12, 1, 15, 0),
                                 )

    def test_404_for_wrong_teacher(self):
        other_teacher = create_teacher()
        wrong_url = reverse('timeline:entry_card', kwargs={
            'username': other_teacher.user.username,
            'pk': self.entry.pk
        })
        response = self.c.get(wrong_url)
        self.assertEquals(response.status_code, 404)

    def test_template_context(self):
        c = Class(
            customer=self.customer,
            lesson_type=self.lesson.get_contenttype(),
        )
        c.assign_entry(self.entry)
        c.save()

        response = self.c.get(self.entry.get_absolute_url())

        with self.assertHTML(response, 'dd') as inf:
            self.assertEquals(inf[0].text, self.teacher.user.crm.full_name)

        with self.assertHTML(response, '.page-header>h1') as (title,):
            self.assertEquals(title.text, str(self.entry))

        with self.assertHTML(response, 'td.timeline-student-list__student') as (student,):
            self.assertIn(self.customer.full_name, student.text)

        with self.assertHTML(response, 'a.timeline-student-list__actions') as (a,):
            del_url = reverse('timeline:delete_customer', kwargs={
                'username': self.teacher.user.username,
                'pk': self.entry.pk,
                'customer': self.customer.pk,
            })
            self.assertEqual(a.attrib.get('href'), del_url)

    def test_list_of_students_to_add(self):
        """
        Check the student selector for adding to the timeline entry
        """
        c1 = Class(
            customer=self.customer,
            lesson_type=self.lesson.get_contenttype(),
        )

        other_customer = create_customer()
        c2 = Class(
            customer=other_customer,
            lesson_type=self.lesson.get_contenttype(),
        )

        c1.assign_entry(self.entry)
        c1.save()

        c2.save()
        response = self.c.get(self.entry.get_absolute_url())
        with self.assertHTML(response, 'select.add-a-student__selector>option') as options:
            self.assertEqual(len(options), 2)  # the first one is 'zero-option'
            self.assertEqual(options[1].attrib.get('value'), reverse('timeline:add_customer', kwargs={
                'username': self.teacher.user.username,
                'pk': self.entry.pk,
                'customer': other_customer.pk,
            }))  # the second — is the student with c2

    def test_add_student_fail_due_to_no_class(self):
        some_other_customer = create_customer()

        url = reverse('timeline:add_customer', kwargs={
            'username': self.teacher.user.username,
            'pk': self.entry.pk,
            'customer': some_other_customer.pk,
        })
        response = self.c.get(url)
        self.assertEqual(response.status_code, 404)  # should throw an error, because customer hasn't any class

    def test_add_student(self):
        c = Class(
            customer=self.customer,
            lesson_type=self.lesson.get_contenttype(),
        )
        c.save()

        self.assertEqual(self.entry.taken_slots, 0)
        self.assertFalse(c.is_scheduled)

        url = reverse('timeline:add_customer', kwargs={
            'username': self.teacher.user.username,
            'pk': self.entry.pk,
            'customer': self.customer.pk,
        })
        print(url)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 302)

        self.entry.refresh_from_db()
        c.refresh_from_db()
        self.assertEqual(self.entry.taken_slots, 1)  # customer now should have been added to a lesson
        self.assertTrue(c.is_scheduled)

    def test_del_student(self):
        c = Class(
            customer=self.customer,
            lesson_type=self.lesson.get_contenttype(),
        )
        c.assign_entry(self.entry)
        c.save()

        self.assertEqual(self.entry.taken_slots, 1)
        self.assertTrue(c.is_scheduled)

        url = reverse('timeline:delete_customer', kwargs={
            'username': self.teacher.user.username,
            'pk': self.entry.pk,
            'customer': self.customer.pk,
        })
        response = self.c.get(url)
        self.assertEqual(response.status_code, 302)
        self.entry.refresh_from_db()
        c.refresh_from_db()

        self.assertEqual(self.entry.taken_slots, 0)
        self.assertFalse(c.is_scheduled)
