from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from moneyed import Money

from payments.models import Payment


def process(request):
    Product = get_object_or_404(ContentType, pk=request.POST['product_type']).model_class()
    product = get_object_or_404(Product, pk=request.POST['product_id'])

    p = Payment(
        product=product,
        cost=Money(request.POST['amount'], request.POST['currency']),
        customer=request.user.crm,
        stripe_token=request.POST['stripeToken'],
    )

    result = p.charge(request)

    resulting_view = 'payments:success'

    if not result:
        resulting_view = 'payments:failure'

    return redirect(
        resolve_url(resulting_view, product_type=int(request.POST['product_type']), product_id=product.pk)
    )


def success(request, product_type, product_id):
    Product = get_object_or_404(ContentType, pk=product_type).model_class()
    product = get_object_or_404(Product, pk=product_id)

    return render(request, product.get_success_template_name(), {
        'product': product,
    })


def failure(request, product_type, product_id):
    return JsonResponse({'result': 'fail'})
