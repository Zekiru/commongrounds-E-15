from django.contrib import admin
from .models import Product, ProductType, Transaction


class ProductInLine(admin.TabularInline):
    model = Product


class ProductTypeAdmin(admin.ModelAdmin):
    model = ProductType
    list_display = [
        'name',
        'description'
    ]
    ordering = ['name']
    inlines = [ProductInLine]


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = [
        'name',
        'product_type',
        'owner',
        'product_image',
        'description',
        'price',
        'stock',
        'status'
    ]
    ordering = ['name']


class TransactionInLine(admin.TabularInline):
    model = Transaction


class TransactionAdmin(admin.ModelAdmin):
    model = Transaction
    list_display = [
        'buyer',
        'product',
        'amount',
        'status',
        'created_on'
    ]


admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Transaction, TransactionAdmin)
