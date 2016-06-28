from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver


class LoginFormTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super(LoginFormTestCase, cls).setUpClass()
        cls.selenium = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LoginFormTestCase, cls).tearDownClass()

    # def testIsFormTwitterBootstrapped(self):
    #     self.selenium.get('%s%s' % (self.live_server_url, '/acc/login/'))
    #     inputs = self.selenium.find_elements_by_css_selector('input.form-control')
    #     self.assertGreaterEqual(len(inputs), 2, 'Login form should have 2 o more twitter bootstrap elements')
