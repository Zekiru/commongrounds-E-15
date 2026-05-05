from django.contrib import admin

from .models import Product, ProductType


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
        'description',
        'price'
    ]
    ordering = ['name']


admin.site.register(ProductType, ProductTypeAdmin)
admin.site.register(Product, ProductAdmin)
