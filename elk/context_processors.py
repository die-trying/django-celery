from django.apps import apps
from django.conf import settings


def support_email(request):
    return {
        'SUPPORT_EMAIL': settings.SUPPORT_EMAIL,
    }


def stripe_pk(request):
    return {
        'STRIPE_PK': settings.STRIPE_PK,
    }


def greeting(request):
    if request.user is None or request.user.id is None:
        return {}

    greeting = request.GET.get('greeting', request.user.crm.get_greeting_type())

    Customer = apps.get_model('crm.Customer')

    try:
        greeting = Customer.clean_greeting(greeting)
    except ValueError:
        greeting = Customer.clean_greeting('empty')

    return {
        'GREETING': greeting
    }


def revision(request):
    return {'REVISION': settings.VERSION}
