from mixer.backend.django import mixer

from elk.utils.testing import ClientTestCase, create_teacher
from timeline.models import Entry as TimelineEntry


class TestFormContext(ClientTestCase):
    """
    Check for a bug: timeline entry edit form should edit entry for the owner
    of the entry, not for the current logged in user.
    """

    def setUp(self):
        self.teacher = create_teacher()

    def test_create_context(self):
        """
        Get create form and check for hidden field 'teacher',
        see template timeline/forms/entry_create.html
        """
        response = self.c.get('/timeline/%s/create/' % self.teacher.user.username)

        with self.assertHTML(response, 'form.form #teacher') as (input,):
            self.assertEquals(input.value, str(self.teacher.pk))

    def test_update_context(self):
        """
        Get update form and check for hidden field 'teacher',
        see template timeline/forms/entry_update.html
        """
        entry = mixer.blend(TimelineEntry, teacher=self.teacher)

        response = self.c.get('/timeline/%s/%d/update/' % (self.teacher.user.username, entry.pk))
        with self.assertHTML(response, 'form.form #teacher') as (input,):
            self.assertEquals(input.value, str(self.teacher.pk))
