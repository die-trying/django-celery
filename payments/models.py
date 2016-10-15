import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from djmoney.models.fields import MoneyField

from payments.stripe import stripe


class Payment(models.Model):
    STRIPE_CURRENCY_MULTIPLIERS = {
        """
        This is a list of multipliers, that convert moneyfield ammount to stripe ammount.

        Stripe accepts only smallest currency units — cents for dollars, копейки for rubles
        see https://support.stripe.com/questions/which-zero-decimal-currencies-does-stripe-support
        """
        'JPY': 1,
    }

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

        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_API_KEY

    def clean(self):
        return True

    def charge(self):
        pass

    def _stripe_amount(self):
        """
        Returns a strip amount — smalles currency unit
        """
        print(str(self.cost.currency))
        multiplyer = self.STRIPE_CURRENCY_MULTIPLIERS.get(str(self.cost.currency), 100)  # default multiplier is 100, 1 USD is 100 cents

        return self.cost.amount * multiplyer
