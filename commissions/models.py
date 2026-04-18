from django.db import models
from django.urls import reverse

from accounts.models import Profile

JOB_STATUS = [
    (0, 'Open'),
    (1, 'Full'),
]
COMMISSION_STATUS = JOB_STATUS + [
    (2, 'Completed'),
    (3, 'Discontinued')
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
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('request_detail', args=[str(self.id)])

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
        return f"{self.role} Role in {self.commission} Commission"

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

    class Meta:
        ordering = [
            'status',
            '-applied_on',
        ]
        verbose_name = 'job application'
        verbose_name_plural = 'job applications'
