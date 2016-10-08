import os

from django.apps import apps
from django.conf import settings


def support_email(request):
    return {
        'SUPPORT_EMAIL': settings.SUPPORT_EMAIL,
    }


def greeting(request):
    if request.user is None or request.user.id is None:
        return {}

    greeting = request.GET.get('greeting', request.user.crm.get_greeting_type())

    Customer = apps.get_model('crm.Customer')

    try:
        greeting = Customer._greeting(greeting)
    except ValueError:
        greeting = Customer._greeting('empty')

    return {
        'GREETING': greeting
    }


def revision(request):
    try:
        f = open(os.path.join(settings.STATIC_ROOT, 'revision.txt'))
        return {
            'REVISION': f.readline().strip()
        }
    except:
        return {
            'REVISION': 'unknown'
        }
