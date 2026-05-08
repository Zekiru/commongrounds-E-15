from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator

from accounts.models import Profile
from cloudinary.models import CloudinaryField


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
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE
    )
    product_image = CloudinaryField(
        'image',
        folder='products/'
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    stock = models.PositiveIntegerField()
    STATUS = [
        ("Available", "Available"),
        ("On sale", "On sale"),
        ("Out of stock", "Out of stock"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Available"
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'merchstore_detail',
            args=[str(self.id)]
        )

    class Meta:
        ordering = ['name']
        verbose_name = 'product'
        verbose_name_plural = 'products'


class Transaction(models.Model):
    buyer = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    STATUS = [
        ("On cart", "On cart"),
        ("To pay", "To pay"),
        ("To ship", "To ship"),
        ("To receive", "To receive"),
        ("Delivered", "Delivered"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS
    )
    created_on = models.DateTimeField(
        auto_now_add=True
    )
