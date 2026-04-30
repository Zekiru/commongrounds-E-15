from django.urls import path
from .views import (
    index,
    RequestListView,
    RequestDetailView,
    RequestCreateView,
    RequestUpdateView,
    JobDetailView,
)

urlpatterns = [
    path('', index, name='index'),
    path(
        'requests/',
        RequestListView.as_view(),
        name='request_list'
    ),
    path(
        'request/<int:pk>/',
        RequestDetailView.as_view(),
        name='request_detail'
    ),
    path(
        'request/create/',
        RequestCreateView.as_view(),
        name='request_create'
    ),
    path(
        'request/<int:pk>/update/',
        RequestUpdateView.as_view(),
        name='request_update'
    ),
    path(
        'job/<int:pk>/',
        JobDetailView.as_view(),
        name='job_detail'
    ),
]
