from django.contrib import admin
from .models import Category, Product, Contacts


@admin.register(Category)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description",)
    search_fields = ("name",)

@admin.register(Product)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "created_at", "updated_at",)
    list_filter = ("category", "price", "created_at", "updated_at",)
    search_fields = ("name", "description", "category__name", "price", "created_at", "updated_at",)

@admin.register(Contacts)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "country", "address", "email",)
    search_fields = ("id", "email",)
