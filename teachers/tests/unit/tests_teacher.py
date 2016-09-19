from elk.utils.testing import TestCase, create_teacher


class TestTeacherUnit(TestCase):
    def test_timeline_url(self):
        teacher = create_teacher()
        self.assertEqual(teacher.timeline_url(), '/timeline/%s/' % teacher.user.username)
