from unittest.mock import MagicMock, patch

import responses
from mixer.backend.django import mixer

from crm.models import Issue
from elk.utils.testing import TestCase, create_customer


class TestIssues(TestCase):
    def setUp(self):
        self.customer = create_customer()

    @responses.activate
    def test_store_issue_to_groove(self):
        responses.add(
            responses.POST,
            'https://api.groovehq.com/v1/tickets',
            body="doesn't matter",
            status=201,
        )

        issue = mixer.blend(Issue, customer=self.customer)
        self.assertEqual(len(responses.calls), 1)

        issue.body = 'sdfsdf'
        issue.save()
        self.assertEqual(len(responses.calls), 1)  # should be only one call

    @responses.activate
    @patch('crm.models.logger')
    def test_store_issue_error(self, logger):
        """
        Check if issue is saved depsite the connection error
        """
        responses.add(
            responses.POST,
            'https://api.groovehq.com/v1/tickets',
            body="doesn't matter",
            status=200,  # not 201, but 200
        )

        logger.error = MagicMock()
        mixer.blend('crm.Issue', customer=self.customer, body='earthquake!')
        self.assertEqual(logger.error.call_count, 1)  # should log an error and save the issue

        issue_that_should_be_saved = Issue.objects.get(customer=self.customer, body='earthquake!')

        self.assertIsNotNone(issue_that_should_be_saved)
