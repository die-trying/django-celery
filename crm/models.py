from django.db import models

from django.contrib.auth.models import User
from django_countries.fields import CountryField

from django.db.models.signals import pre_save
from django.dispatch import receiver

# Create your models here.


class CustomerSource(models.Model):
    name = models.CharField(max_length=140)

    def __str__(self):
        return self.name


class Customer(models.Model):
    LEVELS = [(a + str(i), a + str(i)) for i in range(1, 4) for a in ('A', 'B', 'C')]
    INTERNAL_SOURCE = 1

    user = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True, related_name='crm')

    source = models.ForeignKey(CustomerSource, on_delete=models.PROTECT, default=INTERNAL_SOURCE)
    customer_first_name = models.CharField('First name', max_length=140)
    customer_last_name = models.CharField('Last name', max_length=140)
    customer_email = models.EmailField('Email')

    date_arrived = models.DateTimeField(auto_now_add=True)

    country = CountryField()

    starting_level = models.CharField(max_length=2, db_index=True, choices=LEVELS, default='A1')
    current_level = models.CharField(max_length=2, db_index=True, choices=LEVELS, default='A1')

    def __str__(self):
        return self.full_name

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


@receiver(pre_save, sender=User)
def create_customer(sender, **kwargs):
    user = kwargs.get('instance')
    if not user.pk:
        customer = Customer()
        customer.save()
        user.crm = customer
