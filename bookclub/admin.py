from django.contrib import admin
from .models import BookCategory, Book, BookReview, Bookmark, Borrow


class BookInLine(admin.TabularInline):
    model = Book


class BookCategoryAdmin(admin.ModelAdmin):
    model = BookCategory
    list_display = [
        'name',
        'description'
    ]
    ordering = ['name']
    inlines = [BookInLine]


class BookAdmin(admin.ModelAdmin):
    model = Book
    list_display = [
        'title',
        'author',
        'genre',
        'publication_year'
    ]
    ordering = ['-publication_year']
    readonly_fields = ('created_on', 'updated_on')


class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user_reviewer', 'title')


class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('profile', 'book', 'date_bookmarked')


class BorrowAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrower',
                    'name', 'date_borrowed',
                    'date_to_return')


admin.site.register(BookCategory, BookCategoryAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(BookReview, BookReviewAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Borrow, BorrowAdmin)
