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

    @transaction.atomic
    def create_commission(self, data, jobs_data):
        commission = Commission(
            maker=self.user.profile,
            **data
        )

        jobs = []
        for jd in jobs_data:
            job = Job(commission=commission, **jd)
            job.sync_status()
            jobs.append(job)

        commission.sync_jobs_status(job_list=jobs)

        commission.save()
        Job.objects.bulk_create(jobs)

        return commission

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
        # Fix: Make more concise
        return {
            'pk': commission.pk,
            'title': commission.title,
            'type': commission.type.name if commission.type else None,
            'maker': commission.maker.user.profile,
            'status': commission.get_status,
            'jobs_status': commission.get_jobs_status,
            'people_required': commission.people_required,
            'total_manpower': Coalesce(
                Sum('manpower_required'), 0
            ),
            'open_manpower': Coalesce(
                Sum('manpower_required', filter=Q(status=0)), 0
            )
        }
