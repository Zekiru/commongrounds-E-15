from django.db import models
from django.urls import reverse


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
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    product_type = models.ForeignKey(
        ProductType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
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
