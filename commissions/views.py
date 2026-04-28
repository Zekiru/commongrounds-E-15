from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from extra_views import (
    CreateWithInlinesView,
    UpdateWithInlinesView
)
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (
    Commission,
    Job,
    JobApplication
)
from .forms import (
    CommissionForm,
    JobCreateInline,
    JobUpdateInline,
)
from accounts.mixins import RoleRequiredMixin
from .services import CommissionService


def index(request):
    return redirect('requests/')


class RequestListView(TemplateView):
    template_name = 'commissions/request_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = CommissionService(user=self.request.user)
        context['requests'] = service.get_all_commissions()
        return context


class RequestDetailView(TemplateView):
    template_name = 'commissions/request_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = CommissionService(user=self.request.user)

        commission = service.get_commission(self.kwargs.get('pk'))
        summary = service.get_commission_summary(commission)
        jobs = service.get_jobs_for_commission(commission)
        is_maker = service.is_commission_maker(commission)

        context['request'] = commission
        context['summary'] = summary
        context['jobs'] = jobs
        context['is_maker'] = is_maker

        return context


class RequestCreateView(
    LoginRequiredMixin,
    RoleRequiredMixin,
    CreateWithInlinesView
):
    required_role = 'CM'
    model = Commission
    form_class = CommissionForm
    inlines = [JobCreateInline]
    template_name = 'commissions/request_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def forms_valid(self, form, inlines):
        job_formset = inlines[0]

        try:
            service = CommissionService(user=self.request.user)

            commission_data = form.cleaned_data
            jobs_data = job_formset.get_jobs_data()

            self.object = service.create_commission(
                data=commission_data,
                jobs_data=jobs_data
            )

            return redirect(self.object)
        except Exception as e:
            form.add_error(None, f"Service Error: {e}")
            return self.forms_invalid(form, inlines)


class RequestUpdateView(
    LoginRequiredMixin,
    RoleRequiredMixin,
    UserPassesTestMixin,
    UpdateWithInlinesView
):
    required_role = 'CM'
    model = Commission
    form_class = CommissionForm
    inlines = [JobUpdateInline]
    template_name = 'commissions/request_form.html'

    def test_func(self):
        obj = self.get_object()
        return obj.maker == self.request.user.profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def forms_valid(self, form, inlines):
        job_formset = inlines[0]

        try:
            service = CommissionService(user=self.request.user)
            instance = self.get_object()
            commission_data = form.cleaned_data
            jobs_data = job_formset.get_jobs_data()
            jobs_to_delete = job_formset.get_jobs_to_delete()

            service.update_commission(
                instance,
                commission_data,
                jobs_data,
                jobs_to_delete,
            )

            return redirect(self.object)
        except Exception as e:
            form.add_error(None, f"Update Error: {e}")
            return self.forms_invalid(form, inlines)
