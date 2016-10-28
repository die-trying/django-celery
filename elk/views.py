from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from django.views.generic import DeleteView
from django.views.generic.detail import BaseDetailView


class DelteWithoutConfirmationView(DeleteView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class JSONDetailView(BaseDetailView):
    """
    Render context as a JSON response
    """
    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(data=self.serialize(context), **response_kwargs)

    def serialize(self, context):
        raise ImproperlyConfigured('Please implement serialize() method in your particular view!')
