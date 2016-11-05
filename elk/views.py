from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, DetailView, ListView, TemplateView
from django.views.generic.edit import UpdateView


class DeleteWithoutConfirmationView(DeleteView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class _LoginRequiredViewMixin():
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class LoginRequiredListView(_LoginRequiredViewMixin, ListView):
    pass


class LoginRequiredDetailView(_LoginRequiredViewMixin, DetailView):
    pass


class LoginRequiredTemplateView(_LoginRequiredViewMixin, TemplateView):
    pass


class LoginRequiredUpdateView(_LoginRequiredViewMixin, SuccessMessageMixin, UpdateView):
    pass
