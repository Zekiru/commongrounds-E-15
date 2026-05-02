from django import forms
from .models import Book, BookReview


class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['title', 'comment', 'user_reviewer']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['user_reviewer'].initial = user.profile
            self.fields['user_reviewer'].siabled = True


class BookContributeForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'genre',
            'author', 'synopsis',
            'publication_year', 'available_to_borrow',
            'contributor'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['contributor'].initial = user.profile
            self.fields['contributor'].disabled = True


class BookUpdateForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ['contributor']


class BookFormFactory:
    @classmethod
    def get_form(cls, context):
        forms_map = {
            "review": BookReviewForm,
            "contribute": BookContributeForm,
            "update": BookUpdateForm
        }
        return forms_map.get(context)
