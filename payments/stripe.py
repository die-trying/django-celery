import stripe
from django.conf import settings

STRIPE_CURRENCY_MULTIPLIERS = {
    """
    This is a list of multipliers, that convert moneyfield ammount to stripe ammount.

    Stripe accepts only smallest currency units — cents for dollars, копейки for rubles
    see https://support.stripe.com/questions/which-zero-decimal-currencies-does-stripe-support
    """
    'JPY': 1,
}


def get_stripe_instance():
    """
    Return a pre-configured stripe instance
    """
    stripe.api_key = settings.STRIPE_API_KEY

    return stripe


def stripe_amount(cost):
    """
    Returns a strip amount — smalles currency unit
    """
    multiplyer = STRIPE_CURRENCY_MULTIPLIERS.get(str(cost.currency), 100)  # default multiplier is 100, 1 USD is 100 cents

    return int(cost.amount) * multiplyer
