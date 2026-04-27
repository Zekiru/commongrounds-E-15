from django import forms
from extra_views import InlineFormSetFactory
from django.forms import (
    BaseInlineFormSet,
    inlineformset_factory
)

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


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'status' in self.fields:
            self.fields['commission'].disabled = True
            self.fields['status'].disabled = True


class BaseJobFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        valid_forms = [
            f for f in self.forms
            if f.cleaned_data and not f.cleaned_data.get(
                'DELETE'
            )
        ]

        if len(valid_forms) < 1:
            raise forms.ValidationError(
                'At least one job is required.'
            )

    def get_jobs_data(self):
        return [
            f.cleaned_data for f in self.forms
            if f.cleaned_data and not f.cleaned_data.get('DELETE')
        ]

    def get_jobs_to_delete(self):
        return [
            f.cleaned_data for f in self.forms
            if f.cleaned_data and f.cleaned_data.get('DELETE')
        ]


class JobCreateInline(InlineFormSetFactory):
    model = Job
    form_class = JobForm
    formset_class = BaseJobFormSet
    factory_kwargs = {
        'extra': 1,
        'can_delete': False
    }


class JobUpdateInline(InlineFormSetFactory):
    model = Job
    form_class = JobForm
    formset_class = BaseJobFormSet
    factory_kwargs = {
        'extra': 0,
        'can_delete': True
    }
