from django.apps import apps

from elk.utils.testing import TestCase, create_customer, create_teacher


class TestFixtures(TestCase):
    """
    Test if my fixtures helper generates fixtures with correct relations
    """
    def test_create_customer(self):
        Customer = apps.get_model('crm.customer')
        customer = create_customer()

        self.assertEquals(Customer.objects.get(user__username=customer.user.username), customer)

    def test_create_teacher(self):
        Teacher = apps.get_model('teachers.teacher')
        teacher = create_teacher()

        t = Teacher.objects.get(user__username=teacher.user.username)
        self.assertEqual(t, teacher)
        self.assertIsNotNone(t.user.crm)
        self.assertTrue(t.user.is_staff)

    def test_create_teacher_all_lessons(self):
        teacher = create_teacher()
        allowed_lessons = teacher.allowed_lessons.all()
        self.assertGreater(allowed_lessons.count(), 0)
        self.assertEqual(allowed_lessons[0].app_label, 'lessons')
