from django.db import models
from django.urls import reverse


class CommissionType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = 'commission type'
        verbose_name_plural = 'commission types'


class Commission(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    people_required = models.IntegerField()
    commission_type = models.ForeignKey(
        CommissionType,
        on_delete=models.CASCADE,
        related_name='commissions'
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('request_detail', args=[str(self.id)])

    class Meta:
        ordering = ["created_on"]
        verbose_name = 'commission'
        verbose_name_plural = 'commissions'
