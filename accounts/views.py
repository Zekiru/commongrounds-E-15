from django.views.generic import UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Profile

from merchstore.models import Product
from localevents.models import Event
from bookclub.models import Book
from diyprojects.models import Project
from commissions.models import Commission


class ProfileDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/account_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile

        context['products'] = Product.objects.filter(owner=profile)
        context['events'] = Event.objects.filter(organizer=profile)
        context['books'] = Book.objects.filter(contributor=profile)
        context['projects'] = Project.objects.filter(creator=profile)
        context['commissions'] = Commission.objects.filter(maker=profile)
        
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = "accounts/account_update.html"
    fields = ['display_name', 'role']

    def get_object(self):
        return self.request.user.profile

    def get_success_url(self):
        return reverse_lazy('home')
