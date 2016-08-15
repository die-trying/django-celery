import os

from django.conf import settings


def support_email(request):
    return {
        'SUPPORT_EMAIL': settings.SUPPORT_EMAIL,
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
