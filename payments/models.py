import uuid

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
        return True

    def charge(self):
        result = self._charge_stripe()
        if result:
            self.purchase_product()

    def purchase_product(self):
        return True

    def _charge_stripe(self):
        try:
            self.stripe.Charge.create(
                amount=stripe_amount(self.cost),
                currency=str(self.cost.currency),
                source=self.stripe_token,
                description=self.product.name,
                idempotency_key=self.uuid,
            )
        except:
            logger.error('Stripe charging error', ext_info=True)
            return False

        return True

    def _stripe_amount(self):
        """
        Returns a strip amount — smalles currency unit
        """
        print(str(self.cost.currency))
        multiplyer = self.STRIPE_CURRENCY_MULTIPLIERS.get(str(self.cost.currency), 100)  # default multiplier is 100, 1 USD is 100 cents

        return self.cost.amount * multiplyer
