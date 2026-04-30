from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = "accounts/account_update.html"
    fields = ['display_name', 'role']

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        return reverse_lazy('home')
