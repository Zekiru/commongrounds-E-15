from django.shortcuts import (
    redirect,
    get_object_or_404
)
from django.core.exceptions import PermissionDenied
from django.views.generic import (
    TemplateView,
    UpdateView
)
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
    JobApplicationForm
)
from accounts.mixins import RoleRequiredMixin
from .services import CommissionService


def index(request):
    return redirect('request_list')


class MakerOnlyMixin:
    def is_maker(self, commission):
        return self.request.user.profile == commission.maker


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

        context['request'] = commission
        context['summary'] = service.get_commission_summary(commission)
        context['jobs'] = service.get_jobs_of_commission(commission)
        context['is_maker'] = service.is_maker_of_commission(commission)

        return context

    def post(self, request, *args, **kwargs):
        job_id = request.POST.get('job_id')
        job = get_object_or_404(Job, pk=job_id)
        service = CommissionService(user=request.user)

        try:
            service.apply_to_job(applicant=request.user.profile, job=job)
        except Exception as e:
            raise PermissionDenied(str(e))

        return redirect(job.commission.get_absolute_url())


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
        service = CommissionService(user=self.request.user)
        job_formset = inlines[0]

        try:
            commission_data = form.cleaned_data
            jobs_data = job_formset.get_jobs_data()

            self.object = service.create_commission(
                data=commission_data,
                jobs_data=jobs_data
            )

            return redirect(self.object)
        except Exception as e:
            print(f"DEBUG: Error caught in view: {e}")
            form.add_error(None, f"Service Error: {e}")
            return self.forms_invalid(form, inlines)


class RequestUpdateView(
    LoginRequiredMixin,
    RoleRequiredMixin,
    MakerOnlyMixin,
    UserPassesTestMixin,
    UpdateWithInlinesView
):
    required_role = 'CM'
    model = Commission
    form_class = CommissionForm
    inlines = [JobUpdateInline]
    template_name = 'commissions/request_form.html'

    def test_func(self):
        return (
            self.has_required_role() and
            self.is_maker(self.get_object())
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def forms_valid(self, form, inlines):
        service = CommissionService(user=self.request.user)
        job_formset = inlines[0]

        try:
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
            form.add_error(None, f"Service Error: {e}")
            return self.forms_invalid(form, inlines)


class JobDetailView(
    LoginRequiredMixin,
    RoleRequiredMixin,
    MakerOnlyMixin,
    UserPassesTestMixin,
    UpdateView
):
    required_role = 'CM'
    model = Job
    form_class = JobApplicationForm
    template_name = 'commissions/job_detail.html'

    def test_func(self):
        return (
            self.has_required_role() and
            self.is_maker(self.get_object().commission)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = CommissionService(user=self.request.user)
        job = self.get_object()

        context['commission'] = job.commission
        context['job'] = job
        context['applications'] = service.get_applications_of_job(job)
        context['summary'] = service.get_job_summary(job)

        return context

    def post(self, request, *args, **kwargs):
        service = CommissionService(user=request.user)

        job = self.get_object()
        application_id = request.POST.get('application_id')
        application_status = request.POST.get('application_status')
        application = get_object_or_404(
            JobApplication,
            pk=application_id
        )

        try:
            service.application_review_process(
                application=application,
                status=int(application_status)
            )
        except Exception as e:
            raise PermissionDenied(str(e))

        return redirect(job.get_absolute_url())
