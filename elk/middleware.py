from django.utils import timezone

from elk.geoip import GeoIP


class TimezoneMiddleware():
    def process_request(self, request):
        if request.user is not None and hasattr(request.user, 'crm'):
            tz = request.user.crm.timezone
            timezone.activate(tz)


class SaveRefMiddleWare():
    def process_request(self, request):
        if request.GET.get('ref') is not None and request.session.get('ref') is None:
            request.session['ref'] = request.GET['ref']


class MarkTrialMiddleWare():
    def process_request(self, request):
        if request.user is None or request.user.id is None:
            if 'trial' in request.GET.keys():
                request.session['trial'] = True


class GuessCountryMiddleWare():
    def process_request(self, request):
        if request.session.get('country') is None:
            ip = request.META.get('REMOTE_ADDR')
            try:
                g = GeoIP(ip)
            except BaseException:
                return

            request.session['country'] = g.country

            if request.user is None or request.user.id is None:
                request.session['guessed_timezone'] = g.timezone
