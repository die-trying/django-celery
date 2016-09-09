#from django.contrib.auth.models import User
from elk.utils.testing import ClientTestCase, create_customer


class TestTimezoneMiddleware(ClientTestCase):
    def setUp(self):
        self.customer = create_customer(timezone='Africa/Addis_Ababa')
        self.customer.user.username = 'timezone_tester'
        self.customer.user.set_password('123')
        self.customer.user.save()

        self.c.logout()
        self.c.login(username='timezone_tester', password='123')

    def test_timezone_template_context(self):
        self.assertIsNotNone(self.customer.timezone)

        response = self.c.get('/')

        self.assertEqual(response.context['user'], self.customer.user)  # we should now be logged in with generated user, not the default one
        self.assertEqual(response.context['TIME_ZONE'], 'Africa/Addis_Ababa')

# this tests are commented out since there is no navbar for students
# we'll uncomennt the when moving from vCita back to our scheduling system

# class TestNavBar(ClientTestCase):
#     """
#     Login with 2 different users: teacher(superuser) and a student.
#     Teacher should see a link to his own timeline, and a student should not.
#     """
#     def setUp(self):
#         self.student = User.objects.create_user('student', 'te@ss.a', '123')
#         self.teacher = User.objects.create_superuser('teacher', 'te@ss.a', '123')
#
#     def testNavBarPublicArea(self):
#         self.c.login(username='student', password='123')
#         response = self.c.get('/')
#         self.assertEqual(response.status_code, 200)
#
#         links = self.__get_navbar_links(response)
#
#         self.assertNotIn('/timeline/student/', links)
#         self.assertIn('/history/payments/', links)
#
#     def testNavBarPrivateArea(self):
#         self.c.login(username='teacher', password='123')
#         response = self.c.get('/')
#         self.assertEqual(response.status_code, 200)
#
#         links = self.__get_navbar_links(response)
#         self.assertIn('/timeline/teacher/', links)
#         self.assertIn('/history/payments/', links)
#
#     def __get_navbar_links(self, response):
#         with self.assertHTML(response, 'nav li>a') as links:
#             result = []
#             for link in links:
#                 result.append(link.attrib.get('href'))
#             return result
