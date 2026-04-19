from django import forms

from .models import CommissionType, Commission, Job, JobApplication


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        exclude = ['maker']