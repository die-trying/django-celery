import stripe
from django.conf import settings


def get_stripe():
    """
    Return a pre-configured stripe instance
    """
    stripe.api_key = settings.STRIPE_API_KEY

    return stripe
