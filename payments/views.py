import stripe
from django.conf import settings


# Create your views here.


def process(request):
    stripe.api_key = settings.STRIPE_API_KEY
    stripe.Charge.create(
        amount=10000,
        currency='USD',
        source=request.POST.get('stripeToken'),
        description='Descr example'
    )
