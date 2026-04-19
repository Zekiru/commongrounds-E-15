from django.db import transaction
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce

from .models import (
    Commission,
    Job,
    JobApplication
)


class CommissionService:
    @staticmethod
    def get_all_commissions():
        return Commission.objects.all()

    @staticmethod
    def get_commission(pk):
        try:
            return Commission.objects.get(pk=pk)
        except Commission.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_commission(author, data, jobs_data):
        commission = Commission.objects.create(
            maker=author,
            **data
        )

        jobs = [
            Job(
                commission=commission,
                **job_data
            ) for job_data in jobs_data
        ]

        Job.objects.bulk_create(jobs)

        return commission

    @staticmethod
    def apply_to_job(applicant, job):
        invalid_conditions = [
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

    @staticmethod
    def sync_commission_status(commission):
        if commission.status > 1:
            return

        has_job_openings = commission.jobs.filter(status=0).exists()

        new_status = 0 if has_job_openings else 1

        if commission.status != new_status:
            commission.status = new_status
            commission.save(update_fields=['status'])

    @staticmethod
    def get_commission_summary(commission):
        return {
            'pk': commission.pk,
            'title': commission.title,
            'type': commission.type.name if commission.type else None,
            'maker': commission.maker.user.username,
            'status': dict(Commission.STATUSES).get(
                commission.status, "Unknown"
            ),
            'people_required': commission.people_required,
            'total_manpower': Coalesce(
                Sum('manpower_required'), 0
            ),
            'open_manpower': Coalesce(
                Sum('manpower_required', filter=Q(status=0)), 0
            )
        }
