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
    CommissionForm
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

    def form_valid(self, form):
        service = CommissionService(user=self.request.user)
        try:
            commission_data = form.cleaned_data
            commission_data.pop('maker', None)
            commission_data.pop('job_status', None)

            self.object = service.create_commission(
                data=commission_data,
                jobs_data=[
                    # TO-DO: Implement the creation of Jobs.
                    # Placeholder:
                    {
                        'role': 'Placeholder Role',
                        'manpower_required': 1,
                    },
                ]
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

    def form_valid(self, form):
        service = CommissionService(user=self.request.user)
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
