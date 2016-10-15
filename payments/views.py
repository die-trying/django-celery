from payments.models import Payment
from products.models import Product1


# Create your views here.


def process(request):
    product = Product1.objects.get(pk=1)

    p = Payment(
        product=product,
        cost=product.cost,
        customer=request.user.crm,
        stripe_token=request.POST['stripeToken'],
    )

    p.save()

    p.charge()
