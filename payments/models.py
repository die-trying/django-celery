import uuid

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from djmoney.models.fields import MoneyField

from elk.logging import logger
from payments.stripe import get_stripe_instance, stripe_amount


class Payment(models.Model):
    customer = models.ForeignKey('crm.Customer', related_name='payments', editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    product_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, limit_choices_to={'app_label': 'products'})
    product_id = models.PositiveIntegerField()
    product = GenericForeignKey('product_type', 'product_id')

    cost = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    is_complete = models.BooleanField(default=False)

    stripe_token = models.CharField(max_length=140, editable=False)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.stripe = get_stripe_instance()

    def clean(self):
        """
        Use this method to run pre-charge checks
        """
        return True

    def charge(self, request=None):
        """
        Query stripe for charging
        """
        result = self._charge_by_stripe()
        if result:
            self.save()
            self._log_payment_event(request)
            self.ship()

    def ship(self):
        """
        Actualy ship the product to the customer
        """
        self.product.ship(self.customer)

    def _log_payment_event(self, request):
        PaymentEvent = apps.get_model('history.PaymentEvent')
        ev = PaymentEvent(
            customer=self.customer,
            product=self.product,
            price=self.cost,
            payment=self,
        )
        ev.request = request
        ev.save()

    def _charge_by_stripe(self):
        try:
            self.stripe.Charge.create(
                amount=stripe_amount(self.cost),
                currency=str(self.cost.currency),
                source=self.stripe_token,
                description=self.product.name,
                idempotency_key=self.uuid,
            )
        except:
            logger.error('Stripe charging error')
            return False

        return True
