from django import forms
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


class BaseJobFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # Ensure at least one job is provided
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


JobFormSetCreate = inlineformset_factory(
    Commission, Job,
    formset=BaseJobFormSet,
    fields='__all__',
    extra=0,
    can_delete=False
)


JobFormSetUpdate = inlineformset_factory(
    Commission, Job,
    formset=BaseJobFormSet,
    fields='__all__',
    extra=0,
    can_delete=True
)
