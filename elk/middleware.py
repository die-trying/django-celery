import pytz
from django.conf import settings
from django.utils import timezone


class TimezoneMiddleware():
    def process_request(self, request):
        tzname = request.session.get('django_timezone', settings.TIME_ZONE)
        tzname = 'Europe/Moscow'
        timezone.activate(pytz.timezone(tzname))
        print('Activated timezone', tzname)
        print(timezone.now())
