from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Product, Transaction
from accounts.mixins import RoleRequiredMixin
from .forms import TransactionForm


def index(request):
        return redirect('items/')


class ProductListView(ListView):
    model = Product
    template_name = "merchstore/product_list.html"
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            user_products = Product.objects.filter(owner=self.request.user.profile)
            all_products = Product.objects.exclude(owner=self.request.user.profile)
        else:
            user_products = []
            all_products = Product.objects.all()

        context['user_products'] = user_products
        context['all_products'] = all_products
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "merchstore/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TransactionForm()
        return context
   
    def post(self, request, pk):
        product = Product.objects.get(pk=pk)
        form = TransactionForm(request.POST)

        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if product.owner == request.user.profile:
            return redirect('merchstore_detail', pk=product.pk)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.buyer = request.user.profile
            transaction.product = product
            transaction.status = "OC"

            if product.stock <= 0:
                return redirect('merchstore_detail', pk=product.pk)

            if product.stock >= transaction.amount:
                product.stock -= transaction.amount

                if product.stock == 0:
                    product.status = "Out of stock"

                product.save()
                transaction.save()

        return redirect('merchstore_cart')


class ProductCreateView(RoleRequiredMixin, LoginRequiredMixin, CreateView):
    model = Product
    required_role = "MS"
    template_name = "merchstore/product_create.html"
    fields = ['name', 'product_type', 'product_image', 'description', 'price', 'stock', 'status']

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        return super().form_valid(form)
   

class ProductUpdateView(RoleRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Product
    required_role = "MS"
    template_name = "merchstore/product_update.html"
    fields = ['name', 'product_type', 'product_image', 'description', 'price', 'stock', 'status']

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user.profile)

    def form_valid(self, form):
        if form.instance.stock == 0:
            form.instance.status = "Out of stock"
        else:
            form.instance.status = "Available"
        return super().form_valid(form)


class CartView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "merchstore/cart_view.html"
    context_object_name = "transactions"

    def get_queryset(self):
        return Transaction.objects.filter(buyer=self.request.user.profile)


class TransactionsListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "merchstore/transaction_list.html"
    context_object_name = "transactions"

    def get_queryset(self):
        return Transaction.objects.filter(product__owner=self.request.user.profile) #double underscore finds owner in product model
