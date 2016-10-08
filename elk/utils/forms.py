from django.http import JsonResponse


class AjaxResponseMixin():
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    https://docs.djangoproject.com/en/dev/topics/class-based-views/generic-editing/#ajax-example
    """
    def get_success_url(self):
        return '/'

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        super().form_valid(form)

        data = {
            'pk': self.object.pk,
        }
        return JsonResponse(data)
