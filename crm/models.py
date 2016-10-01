from django.apps import apps
from django.contrib.auth.models import User
from django.db import models
from django_countries.fields import CountryField
from image_cropping import ImageRatioField
from image_cropping.templatetags.cropping import cropped_thumbnail
from timezone_field import TimeZoneField

from crm.signals import trial_lesson_added


class Company(models.Model):
    name = models.CharField(max_length=140)
    legal_name = models.CharField(max_length=140)

    def __str__(self):
        return '%s (%s)' % (self.name, self.legal_name)

    class Meta:
        verbose_name_plural = 'companies'


class CustomerSource(models.Model):
    name = models.CharField(max_length=140)

    def __str__(self):
        return self.name


class Customer(models.Model):
    """
    A model for a base customer.

    Contents everything, related to CRM via properties:
        * payments: payment history: :model:`history.PaymentEvent`
        * classes: all purchased classes: :model:`market.Class`
        * subscriptions: all purchased subscriptions: :model:`market.Subscription`

    The model automatically assigned to a current user, so you can access all CRM properties via `request.user.crm`.
    """
    LEVELS = [(a + str(i), a + str(i)) for i in range(1, 4) for a in ('A', 'B', 'C')]

    user = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True, related_name='crm')

    curator = models.ForeignKey('teachers.Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='patronized_customers')
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')

    source = models.CharField(max_length=140, default='internal')

    customer_first_name = models.CharField('First name', max_length=140, blank=True)
    customer_last_name = models.CharField('Last name', max_length=140, blank=True)
    customer_email = models.EmailField('Email', blank=True)

    date_arrived = models.DateTimeField(auto_now_add=True)
    birthday = models.DateField(null=True, blank=True)

    timezone = TimeZoneField(default='Europe/Moscow')

    ref = models.CharField('Referal code', max_length=140, blank=True)

    cancellation_streak = models.SmallIntegerField('Cancelled lesson streak', default=0)
    max_cancellation_count = models.SmallIntegerField('Maximum allowed lessons to cancel', default=7)

    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    profile_photo_cropping = ImageRatioField('profile_photo', '80x80')

    profession = models.CharField(max_length=140, null=True, blank=True)

    country = CountryField()
    native_language = models.CharField(max_length=140, null=True, blank=True)
    languages = models.ManyToManyField('lessons.Language', blank=True)

    starting_level = models.CharField(max_length=2, choices=LEVELS, blank=True, null=True)
    current_level = models.CharField(max_length=2, choices=LEVELS, blank=True, null=True)

    phone = models.CharField('Phone number', max_length=15, blank=True)
    skype = models.CharField('Skype login', max_length=140, blank=True)
    facebook = models.CharField('Facebook profile id', max_length=140, blank=True)
    twitter = models.CharField('Twitter username', max_length=140, blank=True)
    instagram = models.CharField('Instagram username', max_length=140, blank=True)
    linkedin = models.CharField('Linkedin username', max_length=140, blank=True)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    @property
    def email(self):
        return self._get_user_property('email')

    @property
    def first_name(self):
        return self._get_user_property('first_name')

    @property
    def last_name(self):
        return self._get_user_property('last_name')

    def get_profile_photo(self):
        """
        Get, if exists, profile photo link
        """
        if self.profile_photo:
            return cropped_thumbnail(context={}, instance=self, ratiofieldname='profile_photo_cropping')
        return ''

    def add_trial_lesson(self):
        """
        Add a free trial lesson to the customer
        """
        TrialLesson = apps.get_model('lessons.TrialLesson')
        self.classes.create(
            lesson=TrialLesson.get_default()
        )
        trial_lesson_added.send(sender=self)

    def is_trial_user(self):
        """
        Returns true if the only lesson off this user is trial. And it is not used.

        Will return True when the trial lesson is just finished, because it will be
        marked as finished after an hour. Let it be so.
        """
        if self.classes.count() == 1:
            TrialLesson = apps.get_model('lessons.TrialLesson')
            if isinstance(self.classes.first().lesson, TrialLesson):
                if not self.classes.first().is_fully_used:
                    return True

        return False

    def trial_lesson_is_scheduled(self):
        """
        Check if trial customer has scheduled his lesson
        """
        if not self.is_trial_user():
            return False

        c = self.classes.first()

        return c.is_scheduled

    def _get_user_property(self, property):
        """
        Some properties are stored in the stock Django user model. This method
        fetches a property from the user model if user is composited,
        and fetches a customer field if not.

        Please don't forget to exclude this fields from admin form defined in
        `crm.admin`
        """
        if self.user:
            return getattr(self.user, property)
        return getattr(self, 'customer_' + property)

    def __str__(self):
        return self.full_name

    def can_cancel_classes(self):
        """
        Determine, if user can cancel a particular class. Class here is for future
        purposes.
        """
        if self.cancellation_streak < self.max_cancellation_count:
            return True
        return False

    def can_schedule_classes(self):
        """
        Determine, if user has purchased classes
        """
        if self.classes.filter(is_fully_used=False).exclude(is_scheduled=True).count():
            return True
        return False

    class Meta:
        verbose_name = 'Profile'


class CustomerNote(models.Model):
    teacher = models.ForeignKey('teachers.Teacher', related_name='customer_notes')
    customer = models.ForeignKey(Customer, related_name='notes')
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Customer notes"
