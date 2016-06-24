from django.test import TestCase
import products.models as models
import inspect

# Create your tests here.


class ProductTestCase(TestCase):

    def testHasAllDefinedLessons(self):
        """
        Test every product has LESSONS tuple in it, defining all lesson properties
        """
        for name, member in inspect.getmembers(models):
            if inspect.isclass(member) and member.__bases__[0] == models.Product:
                self.assertTrue(hasattr(member, 'LESSONS'), 'Every Product in product.models should have LESSONS attribute. %s does not' % name)
                for lesson in member.LESSONS:
                    self.assertTrue(hasattr(member, lesson), 'Every Lesson defined in LESSONS should have an ATTR. %s in %s does not' % (lesson, name))
