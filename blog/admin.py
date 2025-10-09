from django.contrib import admin
from .models import Author, Blogpost


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email",)
    search_fields = ("first_name", "last_name", "email",)


@admin.register(Blogpost)
class BlogpostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at",
                    "updated_at", "is_published", "number_of_views",)
    list_filter = ("author", "created_at", "updated_at", "is_published", "number_of_views")
    search_fields = ("id", "title",)
