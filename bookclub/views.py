from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_date
from django import forms

from .forms import BookFormFactory
from .models import Book, BookReview, Bookmark, Borrow
from accounts.mixins import RoleRequiredMixin


def index(request):
    return redirect('books/')


class BookListView(ListView):
    model = Book
    template_name = "bookclub/book_list.html"
    context_object_name = 'all_books'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            profile = self.request.user.profile
            context['books_contributed'] = Book.objects.filter(
                contributor=profile)
            context['books_bookmarked'] = Book.objects.filter(
                bookmark__profile=profile)
            context['books_reviewed'] = Book.objects.filter(
                bookreview__user_reviewer=profile).distinct()

            exclude_ids = (
                list(context[
                    'books_contributed'].values_list('id', flat=True)) +
                list(context[
                    'books_bookmarked'].values_list('id', flat=True)) +
                list(context[
                    'books_reviewed'].values_list('id', flat=True))
            )
            context['all_books'] = Book.objects.exclude(id__in=exclude_ids)
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = "bookclub/book_detail.html"
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_available'] = self.object.available_to_borrow
        context['bookmark_count'] = Bookmark.objects.filter(
            book=self.object).count()
        context['reviews'] = BookReview.objects.filter(book=self.object)

        if self.request.user.is_authenticated:
            context['user_has_bookmarked'] = Bookmark.objects.filter(
                book=self.object,
                profile=self.request.user.profile
            ).exists()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if (
            'action' in request.POST and
            request.POST.get('action') == 'bookmark'
        ):
            if request.user.is_authenticated:
                bookmark, created = Bookmark.objects.get_or_create(
                    profile=request.user.profile,
                    book=self.object
                )
                if not created:
                    bookmark.delete()
            return redirect('bookclub:book_detail', pk=self.object.pk)

        title = request.POST.get('title')
        comment = request.POST.get('comment')

        if title and comment:
            review = BookReview(
                book=self.object,
                title=title,
                comment=comment
            )

            if request.user.is_authenticated:
                review.user_reviewer = request.user.profile
            else:
                review.anon_reviewer = "Anonymous"

            review.save()
        return redirect('bookclub:book_detail', pk=self.object.pk)


class BookCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Book
    template_name = 'bookclub/book_add.html'
    required_role = "BC"

    def get_form_class(self):
        return BookFormFactory.get_form("contribute")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('bookclub:book_detail', kwargs={'pk': self.object.pk})


class BookUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Book
    template_name = 'bookclub/book_edit.html'
    required_role = "BC"

    def get_form_class(self):
        return BookFormFactory.get_form("update")

    def get_success_url(self):
        return reverse('bookclub:book_detail', kwargs={'pk': self.object.pk})


class BookBorrowView(CreateView):
    model = Borrow
    fields = ['date_borrowed', 'name']
    template_name = 'bookclub/book_borrow.html'

    def dispatch(self, request, *args, **kwargs):
        self.book = get_object_or_404(Book, pk=self.kwargs.get('pk'))
        if not self.book.available_to_borrow:
            return redirect('bookclub:book_detail', pk=self.book.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            profile = getattr(self.request.user, 'profile', None)
            initial['name'] = (
                profile.display_name if profile
                else self.request.user.username)
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date_borrowed'].widget = forms.DateInput(
            attrs={'type': 'date'})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.book
        context['return_date_preview'] = (
            timezone.now().date() + timedelta(days=14))
        return context

    def form_valid(self, form):
        form.instance.book = self.book

        if self.request.user.is_authenticated:
            profile = getattr(self.request.user, 'profile', None)
            if profile:
                form.instance.borrower = profile

        borrow_date = form.cleaned_data['date_borrowed']
        form.instance.date_to_return = borrow_date + timedelta(days=14)

        self.book.available_to_borrow = False
        self.book.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'bookclub:book_detail',
            kwargs={'pk': self.kwargs['pk']})

    def post(self, request, *args, **kwargs):
        self.object = None
        if 'calculate' in request.POST:
            form = self.get_form()
            date_str = request.POST.get('date_borrowed')
            context = self.get_context_data(form=form)

            if date_str:
                parsed_date = parse_date(date_str)
                if parsed_date:
                    context['selected_date'] = parsed_date
                    context['date_to_return'] = (
                        parsed_date + timedelta(days=14))
            return self.render_to_response(context)

        return super().post(request, *args, **kwargs)
