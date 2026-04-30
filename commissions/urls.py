from django.urls import path
from .views import index, RequestListView, RequestDetailView

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
]
