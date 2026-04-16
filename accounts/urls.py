from django.urls import path, include
from .views import ProfileUpdateView

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('edit/<str:username>/', ProfileUpdateView.as_view(), name='update'),
]
