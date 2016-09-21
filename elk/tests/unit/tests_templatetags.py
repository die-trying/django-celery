from unittest.mock import MagicMock, patch

import elk.templatetags.custom_humanize as humanize
from elk.utils.testing import TestCase


class TestTemplateTags(TestCase):
    def test_naturaltime_stripping(self):
        with patch('elk.templatetags.custom_humanize.humanize') as mocked_humanize:  # patching stock django 'humanize'
            mocked_humanize.naturaltime = MagicMock(return_value='some staff from now')
            result = humanize.naturaltime(100500)
            self.assertEqual(result, 'some staff')
