from django.urls import path
from . import views

urlpatterns = [
    path('events', views.event_list, name='event_list'),
    path('event/add', views.EventCreateView.as_view(), name='event_create'),
    path('event/<int:event_id>', views.event_detail, name='event_detail'),
    path(
        'event/<int:event_id>/edit',
        views.EventUpdateView.as_view(),
        name='event_update'
    ),
    path(
        'event/<int:event_id>/signup',
        views.EventSignupView.as_view(),
        name='event_signup'
    ),
]
