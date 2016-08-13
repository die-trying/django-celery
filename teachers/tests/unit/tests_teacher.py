from django.test import TestCase

from elk.utils.testing import create_teacher


class TestTeacherUnit(TestCase):
    def test_timeline_url(self):
        teacher = create_teacher()
        self.assertEqual(teacher.timeline_url(), '/timeline/%s/' % teacher.user.username)
