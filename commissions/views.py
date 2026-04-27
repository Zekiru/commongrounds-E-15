from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import (
    Commission,
    Job,
    JobApplication
)
from .forms import (
    CommissionForm,
    JobFormSetCreate,
    JobFormSetUpdate
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
        context['request'] = service.get_commission(
            self.kwargs.get('pk')
        )
        return context


class RequestCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    required_role = 'CM'
    model = Commission
    form_class = CommissionForm
    template_name = 'commissions/request_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['jobs_formset'] = JobFormSetCreate(
                self.request.POST,
            )
        else:
            data['jobs_formset'] = JobFormSetCreate()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['jobs_formset']
        service = CommissionService(user=self.request.user)

        if not formset.is_valid():
            return self.form_invalid(form)

        try:
            commission_data = form.cleaned_data
            jobs_data = [
                f.cleaned_data for f in formset
                if f.cleaned_data and not f.cleaned_data.get(
                    'DELETE'
                )
            ]

            commission_data.pop('maker', None)
            commission_data.pop('job_status', None)
            for job in jobs_data:
                job.pop('commission', None)
                job.pop('status', None)

            print(commission_data)
            print(jobs_data)

            self.object = service.create_commission(
                data=commission_data,
                jobs_data=jobs_data
            )

            return redirect(self.object)
        except Exception as e:
            form.add_error(None, f"Service Error: {e}")
            return self.form_invalid(form)


class RequestUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    required_role = 'CM'
    model = Commission
    form_class = CommissionForm
    template_name = 'commissions/request_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['jobs_formset'] = JobFormSetUpdate(
                self.request.POST,
                instance=self.object
            )
        else:
            data['jobs_formset'] = JobFormSetUpdate(
                instance=self.object
            )
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['jobs_formset']
        service = CommissionService(user=self.request.user)

        if not formset.is_valid():
            return self.form_invalid(form)

        try:
            instance = self.get_object()

            # TO-DO: Implement the updating of Commissions & Jobs.
            # self.object = CommissionService.update_commission(
            #     instance=instance,
            #     data=form.cleaned_data,
            #     jobs_data=[]
            # )

            return redirect(self.object)
        except Exception as e:
            form.add_error(None, f"Update Error: {e}")
            return self.form_invalid(form)
