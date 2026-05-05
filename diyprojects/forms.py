from django import forms
from .models import Project, ProjectReview, ProjectRating


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'category', 'description',
                  'materials', 'steps', 'creator']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile'):
            self.fields['creator'].initial = user.profile
            self.fields['creator'].disabled = True


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['creator']


class ProjectReviewForm(forms.ModelForm):
    class Meta:
        model = ProjectReview
        fields = ['comment', 'image', 'reviewer']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if 'reviewer' in self.fields:
            if user_profile:
                self.fields['reviewer'].initial = user_profile
            self.fields['reviewer'].disabled = True


class ProjectRatingForm(forms.ModelForm):
    class Meta:
        model = ProjectRating
        fields = ['score', 'profile']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['score'].required = True
        if user and hasattr(user, 'profile'):
            self.fields['profile'].initial = user.profile
            self.fields['profile'].disabled = True
