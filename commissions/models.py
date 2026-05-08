from django.db import models
from django.urls import reverse

from accounts.models import Profile

JOB_STATUS = [
    (0, 'Open'),
    (1, 'Full'),
    (2, 'Closed')
]
COMMISSION_STATUS = [
    (0, 'Ongoing'),
    (1, 'Completed'),
    (2, 'Discontinued')
]
APPLICATION_STATUS = [
    (0, 'Pending'),
    (1, 'Accepted'),
    (2, 'Rejected'),
]


class CommissionType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'commission type'
        verbose_name_plural = 'commission types'


class Commission(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.ForeignKey(
        CommissionType,
        null=True,
        on_delete=models.SET_NULL,
        related_name='commissions'
    )
    maker = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='commissions'
    )
    people_required = models.IntegerField()
    status = models.IntegerField(
        choices=COMMISSION_STATUS,
        default=0
    )
    jobs_status = models.IntegerField(
        choices=JOB_STATUS,
        default=0
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('request_detail', kwargs={'pk': self.pk})

    def get_status(self):
        return dict(COMMISSION_STATUS).get(
            self.status, "Unknown"
        )

    def get_jobs_status(self):
        return dict(JOB_STATUS).get(
            self.jobs_status, "Unknown"
        )

    def sync_jobs_status(self, job_list=None):
        new_jobs_status = 2
        if self.status == 0:
            if job_list is not None:
                job_openings = sum(
                    1 for j in job_list if j.status == 0
                )
            else:
                job_openings = self.jobs.filter(status=0).count()
            new_jobs_status = 0 if job_openings > 0 else 1

        if self.jobs_status != new_jobs_status:
            self.jobs_status = new_jobs_status
            return True

        return False

    def set_status(self, status):
        if self.status == status:
            return False

        self.status = status
        self.sync_jobs_status()
        for job in self.jobs.all():
            job.sync_status()
        return True

    class Meta:
        ordering = ['created_on']
        verbose_name = 'commission'
        verbose_name_plural = 'commissions'


class Job(models.Model):
    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    role = models.CharField(max_length=255)
    manpower_required = models.IntegerField()
    status = models.IntegerField(
        choices=JOB_STATUS,
        default=0
    )

    def __str__(self):
        return f"{self.role} in {self.commission}"

    def get_status(self):
        return dict(JOB_STATUS).get(
            self.status, "Unknown"
        )

    def sync_status(self):
        new_status = 2
        if self.commission.status == 0:
            if self.pk is None:
                accepted_applications = 0
            else:
                accepted_applications = self.applications.filter(
                    status=1
                ).count()
            new_status = (
                0 if accepted_applications < self.manpower_required else 1
            )

        if self.status != new_status:
            self.status = new_status
            return True

        return False

    def get_absolute_url(self):
        return reverse('job_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = [
            'status',
            '-manpower_required',
            'role',
        ]
        verbose_name = 'job'
        verbose_name_plural = 'jobs'


class JobApplication(models.Model):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    applicant = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    status = models.IntegerField(
        choices=APPLICATION_STATUS,
        default=0
    )
    applied_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job.role} Application of {self.applicant}"

    def get_status(self):
        return dict(APPLICATION_STATUS).get(
            self.status, "Unknown"
        )

    class Meta:
        ordering = [
            'status',
            '-applied_on',
        ]
        verbose_name = 'job application'
        verbose_name_plural = 'job applications'
