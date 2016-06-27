from django.db import models

from django.contrib.auth.models import User
from django_countries.fields import CountryField

# Create your models here.


class Customer(models.Model):
    LEVELS = [(a + str(i), a + str(i)) for i in range(1, 4) for a in ('A', 'B', 'C')]

    user = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True)

    first_name = models.CharField(max_length=140)
    last_name = models.CharField(max_length=140)
    customer_email = models.EmailField()

    date_arrived = models.DateTimeField(auto_now_add=True)

    country = CountryField()

    starting_level = models.CharField(max_length=2, db_index=True, choices=LEVELS, default='A1')
    current_level = models.CharField(max_length=2, db_index=True, choices=LEVELS, default='A1')

    def __str__(self):
        return self.full_name

    def _get_full_name(self):
        if self.user:
            return '%s %s' % (self.user.first_name, self.user.last_name)

        return '%s %s' % (self.first_name, self.last_name)

    def _get_email(self):
        if self.user:
            return self.user.email
        return self.customer_email

    email = property(_get_email)
    full_name = property(_get_full_name)
