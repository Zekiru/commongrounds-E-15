from django.db import transaction
from django.db.models import Count, Sum, Q
from django.core.exceptions import PermissionDenied

from .models import (
    Commission,
    Job,
    JobApplication
)


class ServiceError(Exception):
    pass


class UnauthorizedAction(PermissionDenied, ServiceError):
    pass


class CommissionValidator:
    def is_authenticated(self):
        return self.user and self.user.is_authenticated

    def is_maker_of_commission(self, commission):
        if not self.is_authenticated():
            return False
        return commission.maker == self.user.profile

    def check_authentication(self):
        if not self.is_authenticated():
            raise UnauthorizedAction(
                "User must be authenticated for this action."
            )

    def check_required_role(self):
        self.check_authentication()
        if not self.user.profile.role == 'CM':
            raise UnauthorizedAction(
                "User does not have the required role for this action."
            )

    def check_maker_of_commission(self, commission):
        self.check_authentication()
        if not self.is_maker_of_commission(commission):
            raise UnauthorizedAction(
                "User must be the maker of this commission for this action."
            )

    def check_matching_total_manpower(self, data, jobs_data):
        commission_total = data.get('people_required', 0)
        job_total = 0
        for jd in jobs_data:
            job_total += jd.get('manpower_required', 0)
        if job_total != commission_total:
            raise ServiceError(
                "People Required does not match Total Job Manpower."
            )


class CommissionFetcher:
    def get_all_commissions(self):
        order = ['status', 'jobs_status', '-created_on']

        all_commissions = Commission.objects.all()
        if not all_commissions.exists():
            return {}

        if not self.is_authenticated():
            return {'all': all_commissions.order_by(*order)}

        created = Commission.objects.filter(
            maker=self.user.profile
        ).order_by(*order)
        applied = Commission.objects.filter(
            jobs__applications__applicant=self.user.profile
        ).distinct().order_by(*order)
        other = Commission.objects.exclude(
            Q(maker=self.user.profile) |
            Q(jobs__applications__applicant=self.user.profile)
        ).distinct().order_by(*order)

        commissions = {}

        if created.exists():
            commissions['created'] = created

        if applied.exists():
            commissions['applied'] = applied

        if other.exists():
            commissions['all'] = other

        return commissions

    def get_commission(self, pk):
        try:
            return Commission.objects.get(pk=pk)
        except Commission.DoesNotExist:
            return None

    def get_jobs_of_commission(self, commission):
        all_jobs = Job.objects.filter(commission=commission).annotate(
            p_count=Count('applications', filter=Q(applications__status=0)),
            a_count=Count('applications', filter=Q(applications__status=1)),
            r_count=Count('applications', filter=Q(applications__status=2))
        )

        category = {'applied': [], 'not_applied': []}

        user_apps = {}
        if self.is_authenticated():
            user_apps = {
                app.job_id: app.get_status()
                for app in JobApplication.objects.filter(
                    job__in=all_jobs,
                    applicant=self.user.profile
                )
            }

        for job in all_jobs:
            job.app_counts = {
                'pending': job.p_count,
                'accepted': job.a_count,
                'rejected': job.r_count,
            }
            job.opening_count = (
                job.manpower_required - job.app_counts['accepted']
            )

            if self.is_authenticated() and job.id in user_apps:
                job.user_status = user_apps[job.id]
                category['applied'].append(job)
            else:
                category['not_applied'].append(job)

        return category

    def get_applications_of_job(self, job):
        return JobApplication.objects.filter(
            job=job
        ).select_related(
            'applicant'
        )


class CommissionService(CommissionValidator, CommissionFetcher):
    def __init__(self, user=None):
        self.user = user

    @transaction.atomic
    def create_commission(self, data, jobs_data):
        self.check_authentication()
        self.check_required_role()
        self.check_matching_total_manpower(
            data=data,
            jobs_data=jobs_data
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
        self.check_authentication()
        self.check_required_role()
        self.check_maker_of_commission(instance)
        self.check_matching_total_manpower(
            data=data,
            jobs_data=jobs_data
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
        self.check_authentication()
        if self.is_maker_of_commission(job.commission):
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

        total_req = commission.jobs.aggregate(
            total=Sum('manpower_required')
        )['total'] or 0

        total_accepted = commission.jobs.aggregate(
            accepted=Count('applications', filter=Q(applications__status=1))
        )['accepted'] or 0

        return {
            'status': status if commission.status != 0 else jobs_status,
            'total_manpower': total_req,
            'closed_manpower': total_accepted,
            'open_manpower': max(0, total_req - total_accepted)
        }

    def get_job_summary(self, job):
        apps_data = job.applications.aggregate(
            pending=Count('id', filter=Q(status=0)),
            accepted=Count('id', filter=Q(status=1)),
            rejected=Count('id', filter=Q(status=2))
        )

        return apps_data

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
