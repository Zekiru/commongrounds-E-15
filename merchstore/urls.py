from django.urls import path
from .views import (
    index, ProductListView, ProductDetailView, 
    ProductCreateView, ProductUpdateView, 
    CartView, TransactionsListView
)

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
    path(
        'item/add/',
        ProductCreateView.as_view(),
        name="merchstore-create"
    ),
    path(
        'item/<int:pk>/edit',
        ProductUpdateView.as_view(),
        name="merchstore-update"
    ),
    path(
        'cart/',
        CartView.as_view(),
        name="merchstore-cart"
    ),
    path(
        'transactions/',
        TransactionsListView.as_view(),
        name="merchstore-transactions"
    ),
]
