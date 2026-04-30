from django.db import transaction
from django.db.models import Sum, Q
from django.core.exceptions import PermissionDenied

from .models import (
    Commission,
    Job,
    JobApplication
)


class ServiceError(Exception):
    pass


class UnauthorizedAction(ServiceError):
    pass


class CommissionService:
    def __init__(self, user=None):
        self.user = user

    def is_authenticated(self):
        return self.user is not None and self.user.is_authenticated

    def has_role(self, role):
        return self.is_authenticated() and self.user.profile.role == role

    def is_commission_maker(self, commission):
        return (
            self.is_authenticated() and
            commission.maker == self.user.profile
        )

    def has_applied_to_job(self, job):
        if not self.is_authenticated():
            return False
        return job.applications.filter(applicant=self.user.profile).exists()

    def get_all_commissions(self):
        def all_commissions():
            return {
                'all': Commission.objects.all().order_by(
                    'status',
                    'jobs_status',
                    '-created_on'
                ),
            }

        if not self.is_authenticated():
            return all_commissions()

        created = Commission.objects.filter(
            maker=self.user.profile
        ).order_by(
            'status',
            'jobs_status',
            '-created_on'
        )
        applied = Commission.objects.filter(
            jobs__applications__applicant=self.user.profile
        ).distinct().order_by(
            'status',
            'jobs_status',
            '-created_on'
        )
        no_groups = not created.exists() and not applied.exists()

        if no_groups:
            return all_commissions()

        other = Commission.objects.exclude(
            Q(maker=self.user.profile) |
            Q(jobs__applications__applicant=self.user.profile)
        ).distinct().order_by(
            'status',
            'jobs_status',
            '-created_on'
        )

        return {
            'created': created,
            'applied': applied,
            'other': other,
        }

    def get_commission(self, pk):
        try:
            return Commission.objects.get(pk=pk)
        except Commission.DoesNotExist:
            return None

    def get_categorized_jobs(self, commission):
        all_jobs = list(Job.objects.filter(commission=commission))

        if not self.user.is_authenticated:
            return {'applied': [], 'not_applied': all_jobs}

        user_apps = {
            app.job_id: app.get_status()
            for app in JobApplication.objects.filter(
                job__in=all_jobs,
                applicant=self.user.profile
            )
        }

        categorized = {
            'applied': [],
            'not_applied': []
        }

        for job in all_jobs:
            if job.id in user_apps:
                job.user_status = user_apps[job.id]
                categorized['applied'].append(job)
            else:
                categorized['not_applied'].append(job)

        return categorized

    def get_applications_for_job(self, job):
        return JobApplication.objects.filter(
            job=job
        ).select_related(
            'applicant'
        )

    @transaction.atomic
    def create_commission(self, data, jobs_data):
        if self.is_authenticated() is False:
            raise UnauthorizedAction(
                "User must be authenticated to create a commission."
            )
        if self.has_role('CM') is False:
            raise UnauthorizedAction(
                "User does not have permission to create a commission."
            )

        data.pop('maker', None)
        data.pop('job_status', None)

        commission = Commission(
            maker=self.user.profile,
            **data
        )

        jobs = []
        for jd in jobs_data:
            jd.pop('commission', None)
            jd.pop('status', None)
            job = Job(commission=commission, **jd)
            job.sync_status()
            jobs.append(job)

        commission.sync_jobs_status(job_list=jobs)

        commission.save()
        Job.objects.bulk_create(jobs)

        return commission

    @transaction.atomic
    def update_commission(
        self,
        instance,
        data,
        jobs_data,
        jobs_to_delete=None
    ):
        if self.is_authenticated() is False:
            raise UnauthorizedAction(
                "User must be authenticated to update a commission."
            )
        if self.has_role('CM') is False:
            raise UnauthorizedAction(
                "User does not have permission to update a commission."
            )
        if self.is_commission_maker(instance) is False:
            raise UnauthorizedAction(
                "User is not the maker of this commission."
            )

        data.pop('maker', None)
        data.pop('job_status', None)
        status = data.pop('status', None)

        if status is not None and instance.set_status(status):
            instance.save()

        for attr, value in data.items():
            setattr(instance, attr, value)

        if jobs_to_delete:
            for job in jobs_to_delete:
                instance.jobs.filter(
                    commission=job['commission'],
                    role=job['role']
                ).delete()

        jobs_to_create = []
        jobs_to_update = []
        all_active_jobs = []

        for jd in jobs_data:
            job_instance = jd.pop('id', None)

            jd.pop('commission', None)
            jd.pop('status', None)
            jd.pop('DELETE', None)

            if job_instance:  # update
                for attr, value in jd.items():
                    setattr(job_instance, attr, value)

                job_instance.sync_status()
                jobs_to_update.append(job_instance)
                all_active_jobs.append(job_instance)
            else:  # create
                new_job = Job(commission=instance, **jd)
                new_job.sync_status()
                jobs_to_create.append(new_job)
                all_active_jobs.append(new_job)

        instance.sync_jobs_status(job_list=all_active_jobs)
        instance.save()

        if jobs_to_create:
            Job.objects.bulk_create(jobs_to_create)

        if jobs_to_update:
            for job in jobs_to_update:
                job.save()

        return instance

    def apply_to_job(self, applicant, job):
        if self.is_authenticated() is False:
            raise UnauthorizedAction(
                "User must be authenticated to apply to a job."
            )
        if self.is_commission_maker(job.commission):
            raise ServiceError(
                "Commission makers cannot apply to their own jobs."
            )

        invalid_conditions = [
            job.applications.filter(applicant=applicant).exists(),
            job.status != 0
        ]

        if any(invalid_conditions):
            return False

        JobApplication.objects.create(
            applicant=applicant,
            job=job,
        )

        return True

    def sync_commission_status(self, commission):
        if commission.sync_jobs_status():
            commission.save()
            return True
        return False

    def get_commission_summary(self, commission):
        status = commission.get_status()
        jobs_status = commission.get_jobs_status()

        manpower_data = commission.jobs.aggregate(
            total=Sum('manpower_required'),
            closed=Sum('manpower_required', filter=Q(status=1)),
        )

        return {
            'status': status if commission.status != 0 else jobs_status,
            'total_manpower': manpower_data['total'] or 0,
            'closed_manpower': manpower_data['closed'] or 0,
            'open_manpower': (
                (manpower_data['total'] or 0) - (manpower_data['closed'] or 0)
            )
        }

    def get_user_application_status(self, jobs):
        if not self.user or self.user.is_anonymous:
            return []

        return list(JobApplication.objects.filter(
            job__in=jobs,
            applicant=self.user.profile
        ).values_list('job_id', flat=True))

    def application_review_process(self, application, status=0):
        if application.status != 0:
            raise UnauthorizedAction(
                "Only pending applications can be reviewed."
            )
        if status not in [0, 1, 2]:
            raise ServiceError(
                "Invalid status for application review."
            )

        if application.status != status:
            application.status = status
            application.save()

        if status == 1:
            job = application.job
            job.sync_status()
            job.save()
            self.sync_commission_status(job.commission)

        return application
