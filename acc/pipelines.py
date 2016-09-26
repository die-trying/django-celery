from abc import ABCMeta, abstractmethod

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from requests import HTTPError, request

from acc.signals import new_user_registered
from crm.models import Customer
from elk.logging import logger


class SaveSocialProfile(metaclass=ABCMeta):
    """
    An abstract class to python-social-auth pipeline for populating
    a User model with app-specific load:
        - Create a user.crm link to a crm.Customer models
        - Fetch profile photo

    The simplest subclass example is SaveGoogleProfile class.
    """
    source_name = 'generic'
    extension = 'jpg'

    def __init__(self, *args, **kwargs):
        self.user = kwargs['user']
        self.response = kwargs['response']
        self.backend = kwargs['backend']

    def run(self):
        customer = Customer()
        customer.save()

        self.user.crm = customer

        self.save_social_source()

        self.fetch_picture()
        self.save_picture()

        self.user.save()

    def fetch_picture(self):
        url = self.get_picture_url()
        try:
            response = request('GET', url)
            response.raise_for_status()
        except HTTPError:
            logger.error('Error fetching user avatar', exc_info=True, extra={'response': response})
        else:
            self.profile_picture = ContentFile(response.content)

    def save_picture(self):
        filename = '%s-%s.%s' % (self.user.username, self.source_name, self.extension)
        self.user.crm.profile_photo.save(filename, self.profile_picture)

    def save_social_source(self):
        self.user.crm.source = self.backend.name

    @abstractmethod
    def get_picture_url(self):
        pass


class SaveGoogleProfile(SaveSocialProfile):
    source_name = 'google'

    def get_picture_url(self):
        return self.response['image'].get('url')


class SaveFacebookProfile(SaveSocialProfile):
    source_name = 'facebook'

    def get_picture_url(self):
        return 'http://graph.facebook.com/%d/picture' % int(self.response['id'])


def save_profile_picture(strategy, backend, user, response, is_new=False, *args, **kwargs):
    """
    A python-social-auth pipeline entry point for running SaveSocialProfile
    class.

    You should add this to the end your SOCIAL_AUTH_PIPELINE in your settings,
    right after built-it pipelines, like this:
        SOCIAL_AUTH_PIPELINE = (
            'social.pipeline.social_auth.social_details',
            ...
            'acc.pipelines.save_profile_picture',
            # your other pipelines
        )
    """
    if not is_new:
        return

    if backend.name == 'google-oauth2':
        profile_saver = SaveGoogleProfile(user=user, response=response, backend=backend)
        profile_saver.run()

    if backend.name == 'facebook':
        profile_saver = SaveFacebookProfile(user=user, response=response, backend=backend)
        profile_saver.run()


def save_country(strategy, backend, user, response, is_new=False, *args, **kwargs):
    """
    Save country guessed by geotargeting
    """
    if not is_new:
        return

    country = strategy.session_get('country')
    if country is not None:
        try:
            user.crm.country = country
            user.crm.save()
        except:
            logger.warning("Incorrect country during self-registration")


def save_timezone(strategy, backend, user, response, is_new=False, *args, **kwargs):
    if not is_new:
        return

    timezone = strategy.session_get('guessed_timezone')

    if timezone is not None:
        try:
            user.crm.timezone = timezone
            user.crm.save()
        except ValidationError:
            logger.warning("Incorrect timezone during self-registration")

    else:
        logger.warning("Could not guess timezone during self-registration")


def save_referral(strategy, backend, user, response, is_new=False, *args, **kwargs):
    """
    Store referral inside the customer model
    """
    if not is_new:
        return

    ref = strategy.session_get('ref')
    if ref is None:
        return

    user.crm.ref = ref
    user.crm.save()


def notify_staff(strategy, backend, user, response, is_new=False, *args, **kwargs):
    """
    Notify SUPPORT_EMAIL and referral about a new student
    """

    if not is_new:
        return

    ref = strategy.session_get('ref')
    if ref is not None:
        try:
            teacher = Customer.objects.get(user__username=ref)  # customers are teachers to
        except:
            pass
        finally:
            new_user_registered.send(sender=notify_staff, user=user, whom_to_notify=teacher.email)

    new_user_registered.send(sender=notify_staff, user=user)
