from django.db import transaction
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce

from .models import (
    Commission,
    Job,
    JobApplication
)


class CommissionService:
    def __init__(self, user=None):
        self.user = user

    def get_all_commissions(self):
        return Commission.objects.all()

    def get_commission(self, pk):
        try:
            return Commission.objects.get(pk=pk)
        except Commission.DoesNotExist:
            return None

    def get_jobs_for_commission(self, commission):
        return commission.jobs.all()

    @transaction.atomic
    def create_commission(self, data, jobs_data):
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
        invalid_conditions = [
            # Fix: These hit the db more than neccessary.
            JobApplication.objects.filter(
                applicant=applicant, job=job
            ).exists(),
            job.commission.status != 0,
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
