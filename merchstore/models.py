from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator

from accounts.models import Profile 


class ProductType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'product type'
        verbose_name_plural = 'product types'


class Product(models.Model):
    name = models.CharField(
        max_length=255
    )
    product_type = models.ForeignKey(
        ProductType, 
        on_delete = models.SET_NULL, 
        null=True,
        blank=True
    )
    owner = models.ForeignKey(
        Profile, on_delete = models.CASCADE
    )
    product_image = models.ImageField(
        upload_to='images/'
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits= 10,
        decimal_places=2
    )
    stock = models.PositiveIntegerField()
    STATUS = {
        "A": "Available",
        "OS": "On sale",
        "OOS": "Out of stock"
    }
    status = models.CharField(
        max_length = 3,
        choices = STATUS,
        default = "A"
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'merchstore-detail',
            args=[str(self.id)]
        )

    class Meta:
        ordering = ['name']
        verbose_name = 'product'
        verbose_name_plural = 'products'

class Transaction(models.Model):
    buyer = models.ForeignKey(
        Profile,
        on_delete = models.SET_NULL,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete = models.CASCADE
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    STATUS = {
        "OC": "On cart",
        "TP": "To pay",
        "TS": "To ship",
        "TR": "To receive",
        "D": "Delivered"
    }
    status = models.CharField(
        max_length = 5,
        choices = STATUS
    )
    created_on = models.DateTimeField(
        auto_now_add=True
    )