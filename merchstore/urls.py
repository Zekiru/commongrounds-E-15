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
        name="merchstore_list"
    ),
    path(
        'item/<int:pk>/',
        ProductDetailView.as_view(),
        name="merchstore_detail"
    ),
    path(
        'item/add/',
        ProductCreateView.as_view(),
        name="merchstore_create"
    ),
    path(
        'item/<int:pk>/edit',
        ProductUpdateView.as_view(),
        name="merchstore_update"
    ),
    path(
        'cart/',
        CartView.as_view(),
        name="merchstore_cart"
    ),
    path(
        'transactions/',
        TransactionsListView.as_view(),
        name="merchstore_transactions"
    ),
]
