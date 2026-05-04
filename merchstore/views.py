from django.shortcuts import redirect
from django.views.generic import ListView, DetailView

from .models import Product


def index(request):
    return redirect('items/')


class ProductListView(ListView):
    model = Product
    template_name = "merchstore/product_list.html"
    context_object_name = 'products'


class ProductDetailView(DetailView):
    model = Product
    template_name = "merchstore/product_detail.html"
