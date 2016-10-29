from django.views.generic import DeleteView


class DelteWithoutConfirmationView(DeleteView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
