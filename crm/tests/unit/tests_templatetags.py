from django.template import Context, Template

from elk.utils.testing import TestCase


class TestContactUsTemplateTag(TestCase):
    def test_default(self):
        tpl = Template("{% load contact_us %}{% contact_us %}")
        html = tpl.render(Context({}))

        self.assertIn('<a href="#" class="" data-toggle="modal" data-target="#issue-popup"', html)

    def test_text(self):
        tpl = Template("{% load contact_us %}{% contact_us 'drop a line' %}")
        html = tpl.render(Context({}))

        self.assertIn('>drop a line</a>', html)

    def test_classes(self):
        tpl = Template("{% load contact_us %}{% contact_us 'drop a line' 'btn btn-lg' %}")
        html = tpl.render(Context({}))

        self.assertIn('class="btn btn-lg"', html)
