from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from djmoney.models.fields import MoneyField

from crm.models import Customer
from market.models import Class

EVENT_SOURCES = (
    ('customer', 'customer'),
    ('teacher', 'Teacher'),
)


class HistoryEvent(models.Model):
    """
    Abstract class for a user-generated history event.
    Every subclass must define a customer relation.

    When creating a history event, you should define a request here for further
    analysis. See examples in history.signals and history.tests.
    """
    time = models.DateTimeField(auto_now_add=True)
    src = models.CharField('Event source', max_length=10, choices=EVENT_SOURCES, default='customer')
    ip = models.GenericIPAddressField(default='127.0.0.1')
    raw_useragent = models.TextField()

    is_mobile = models.NullBooleanField(null=True)
    is_tablet = models.NullBooleanField(null=True)
    is_pc = models.NullBooleanField(max_length=140, null=True)
    browser_family = models.CharField(max_length=140, null=True)
    browser_version = models.CharField(max_length=140, null=True)
    os_family = models.CharField(max_length=140, null=True)
    os_version_string = models.CharField(max_length=140, null=True)
    device = models.CharField(max_length=140, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.__store_request(self.request)
        super().save(*args, **kwargs)

    def __store_request(self, request):
        """
        Store request data for future analysis.
        Relies on https://github.com/selwin/django-user_agents
        """
        for i in ('is_mobile', 'is_tablet', 'is_pc'):
            setattr(self, i, getattr(request.user_agent, i))

        self.browser_family = request.user_agent.browser.family
        self.browser_version = request.user_agent.browser.version_string
        self.os_family = request.user_agent.os.family
        self.os_version = request.user_agent.os.version_string
        self.device = request.user_agent.device.family

        self.ip = request.META.get('REMOTE_ADDR')
        self.raw_useragent = request.META.get('HTTP_USER_AGENT')

    class Meta:
        abstract = True


class ProductEvent(HistoryEvent):
    """
    Abstract class for events with products, like buying
    """
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    product_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    product = GenericForeignKey('product_type', 'product_id')

    class Meta:
        abstract = True


class ClassEvent(HistoryEvent):
    """
    Class for timeline events, like planning or cancelling.
    """
    TYPE_CHOICES = (
        ('SCHED', 'Scheduling'),
        ('CANCEL', 'Cancellation'),
        ('RESCH', 'Rescheduling'),
    )
    event_type = models.CharField('Event type', max_length=5, blank=False, choices=TYPE_CHOICES, db_index=True)
    scheduled_class = models.ForeignKey(Class)


class PaymentEvent(ProductEvent):
    customer = models.ForeignKey(Customer, related_name='payments')
