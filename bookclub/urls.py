from django.urls import path
from . import views

app_name = "bookclub"

urlpatterns = [
    path(
        'books/',
        views.BookListView.as_view(),
        name="book_list"),
    path(
        'book/<int:pk>/',
        views.BookDetailView.as_view(),
        name="book_detail"),
    path(
        'book/add/',
        views.BookCreateView.as_view(),
        name="book_add"),
    path(
        'book/<int:pk>/edit/',
        views.BookUpdateView.as_view(),
        name="book_edit"),
    path(
        'book/<int:pk>/borrow/',
        views.BookBorrowView.as_view(),
        name="book_borrow"),
]
