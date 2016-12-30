from os.path import basename, join

import responses
from mixer.backend.django import mixer

from elk.utils.testing import ClientTestCase, TestCase

from .pipelines import SaveSocialProfile


class TestSaveSocialProfile(SaveSocialProfile):
    source_name = 'testsrc'
    extension = 'jpgtest'

    def get_picture_url(self):
        return 'http://testing.test/testpic.jpg'

    @responses.activate
    def fetch_picture(self):
        return super().fetch_picture()


class TestSocialPipeline(TestCase):
    def setUp(self):
        responses.add(responses.GET,
                      'http://testing.test/testpic.jpg',
                      body=self._read_fixture('me.jpg'),
                      status=200,
                      content_type='image/jpeg'
                      )

    def _read_fixture(self, src):
        src = join('./acc/fixtures/', src)
        return open(src, 'rb').read()

    def test_fetch_picture(self):
        profile_saver = TestSaveSocialProfile(user='', response='', backend='')
        profile_saver.fetch_picture()
        self.assertIsNotNone(profile_saver.profile_picture.read())

    def test_save_source(self):
        user = mixer.blend('auth.User')

        class TestBackend:
            name = 'social-test-source-name'

        profile_saver = TestSaveSocialProfile(user=user, response='', backend=TestBackend)
        profile_saver.fetch_picture()
        profile_saver.save_social_source()

        self.assertEqual(user.crm.source, 'social-test-source-name')

    def test_save_picture(self):
        user = mixer.blend('auth.user')
        responses.add(responses.GET,
                      'http://testing.test/testpic.jpg',
                      body=b'testbytes',
                      status=200,
                      content_type='image/jpeg'
                      )

        profile_saver = TestSaveSocialProfile(user=user, response='', backend='')
        profile_saver.fetch_picture()

        profile_saver.save_picture()

        self.assertEqual(basename(user.crm.profile_photo.name), '%s-testsrc.jpgtest' % user.username)
        self.assertIsNotNone(user.crm.profile_photo)


class TestLoginPage(ClientTestCase):
    def setUp(self):
        self.c.logout()

    def test_login_page_redirect(self):
        response = self.c.get('/')
        self.assertRedirects(response, '/accounts/login/?next=/')

    def test_login_page_200(self):
        response = self.c.get('/accounts/login/?next=/')
        self.assertEqual(response.status_code, 200)
