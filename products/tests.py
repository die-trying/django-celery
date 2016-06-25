from django.test import TestCase
from elk.utils.reflection import find_ancestors

import products.models as models

# Create your tests here.


class ProductTestCase(TestCase):

    def testHasAllDefinedLessons(self):
        """
        Test every product has LESSONS tuple in it, defining all lesson properties
        """
        for product in find_ancestors(models, base_class=models.Product):
            self.assertTrue(hasattr(product, 'LESSONS'), 'Every Product in product.models should have LESSONS attribute. %s does not' % product)
            for lesson in product.LESSONS:
                self.assertTrue(hasattr(product, lesson), 'Every Lesson defined in LESSONS should have an ATTR. %s in %s does not' % (lesson, product))
