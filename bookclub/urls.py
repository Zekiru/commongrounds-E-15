from django.urls import path
from .views import index, BookListView, BookDetailView

urlpatterns = [
    path('', index, name='index'),
    path('books/', BookListView.as_view(), name="book_list"),
    path('book/<int:pk>/', BookDetailView.as_view(), name="book_detail"),
]

app_name = "bookclub"
