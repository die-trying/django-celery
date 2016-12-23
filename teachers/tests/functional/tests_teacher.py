from django.conf import settings

from elk.utils.testing import TestCase, create_teacher


class TestTeacherFunctional(TestCase):
    fixtures = ('crm', 'teachers', 'lessons')

    def setUp(self):
        self.teacher = create_teacher(accepts_all_lessons=False)

    def test_automatic_group_assignment(self):
        """
        All newly created teachers should be members of 'teacher' permission group
        """
        self.assertEqual(self.teacher.user.groups.first().pk, settings.TEACHER_GROUP_ID)
