from django.contrib.gis.geoip import GeoIP
from django.utils import timezone


class TimezoneMiddleware():
    def process_request(self, request):
        if request.user is not None and hasattr(request.user, 'crm'):
            tz = request.user.crm.timezone
            timezone.activate(tz)


class SaveRefMiddleWare():
    def process_request(self, request):
        if request.GET.get('ref') is not None and request.session.get('ref') is None:
            request.session['ref'] = request.GET['ref']


class GuessCountryMiddleWare():
    def process_request(self, request):
        g = GeoIP()
        ip = request.META.get('REMOTE_ADDR')
        country = g.country(ip)
        request.session['country'] = country['country_code']
