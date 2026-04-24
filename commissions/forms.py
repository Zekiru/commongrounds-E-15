from django import forms

from .models import (
    Commission,
    Job,
    JobApplication
)


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['maker'].initial = user.profile

        self.fields['maker'].disabled = True
        self.fields['jobs_status'].disabled = True
