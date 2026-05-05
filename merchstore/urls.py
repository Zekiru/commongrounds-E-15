from django.urls import path
from .views import index, ProductListView, ProductDetailView

urlpatterns = [
    path('', index, name='index'),
    path(
        'items/',
        ProductListView.as_view(),
        name="merchstore-list"
    ),
    path(
        'item/<int:pk>/',
        ProductDetailView.as_view(),
        name="merchstore-detail"
    ),
]
