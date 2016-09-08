from django.utils import timezone


class TimezoneMiddleware():
    def process_request(self, request):
        if request.user is not None:
            tz = request.user.crm.timezone
            timezone.activate(tz)


class SaveRefMiddleWare():
    def process_request(self, request):
        if request.GET.get('ref') is not None and request.session.get('ref') is None:
            request.session['ref'] = request.GET['ref']
