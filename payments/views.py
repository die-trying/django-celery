from payments.models import Payment
from products.models import Product1


# Create your views here.


def process(request):
    product = Product1.objects.get(pk=1)  # FIXME

    p = Payment(
        product=product,
        cost=product.cost,  # FIXME: this value should be taken from tier
        customer=request.user.crm,
        stripe_token=request.POST['stripeToken'],
    )

    p.charge(request)
