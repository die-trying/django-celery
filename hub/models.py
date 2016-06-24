from django.db import models
from crm.models import Customer

from djmoney.models.fields import MoneyField

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class ActiveSubscription(models.Model):
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )
    customer = models.ForeignKey(Customer)

    buy_time = models.DateTimeField(auto_now_add=True)
    buy_price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    active = models.SmallIntegerField(choices=ENABLED, default=1)

    product_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    product = GenericForeignKey('product_type', 'product_id')

    def save(self, *args, **kwargs):
        super(ActiveSubscription, self).save(*args, **kwargs)

        for lesson_type in self.product.LESSONS:
            for lesson in getattr(self.product, lesson_type).all():
                bought_lesson = ActiveLesson(
                    lesson=lesson,
                    subscription=self,
                    customer=self.customer,
                    buy_price=self.buy_price
                )
                bought_lesson.save()


class ActiveLesson(models.Model):
    BUY_SOURCES = (
        (0, 'Single'),
        (1, 'Subscription')
    )
    ENABLED = (
        (0, 'Inactive'),
        (1, 'Active'),
    )

    customer = models.ForeignKey(Customer)

    buy_time = models.DateTimeField(auto_now_add=True)
    buy_price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    buy_source = models.SmallIntegerField(choices=BUY_SOURCES, default=0)

    active = models.SmallIntegerField(choices=ENABLED, default=1)

    lesson_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    lesson_id = models.PositiveIntegerField()
    lesson = GenericForeignKey('lesson_type', 'lesson_id')

    subscription = models.ForeignKey(ActiveSubscription, on_delete=models.CASCADE, null=True)
