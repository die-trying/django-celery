from elk.utils.testing import ClientTestCase, create_customer, create_teacher


class TestTeacherDetail(ClientTestCase):
    def setUp(self):
        self.teacher = create_teacher()

    def test_card_loading(self):
        response = self.c.get('/teachers/%s/' % self.teacher.user.username)

        with self.assertHTML(response, 'img.teacher-face') as teacher_face:
            self.assertIsNotNone(teacher_face)

    def test_no_teacher_card_for_non_teacher_user(self):
        some_random_man = create_customer()
        response = self.c.get('/teachers/%s/' % some_random_man.user.username)

        self.assertEqual(response.status_code, 404)
