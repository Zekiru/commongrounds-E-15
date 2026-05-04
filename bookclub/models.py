from django.db import models


class BookCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']
        verbose_name = 'book category'
        verbose_name_plural = 'book categories'

        def __str__(self):
            return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    genre = models.ForeignKey(
        BookCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    author = models.CharField(max_length=255)
    publication_year = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publication_year']
        verbose_name = 'book'
        verbose_name_plural = 'books'

    def __str__(self):
        return self.title
