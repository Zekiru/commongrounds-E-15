from django.urls import path, include
from .views import ProfileDashboardView, ProfileUpdateView

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('dashboard/', ProfileDashboardView.as_view(), name='dashboard'),
    path('edit/<str:username>/', ProfileUpdateView.as_view(), name='update'),
]
