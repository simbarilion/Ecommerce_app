from django.contrib import admin
from .models import Category, Product, Contacts, MessageFeedback


@admin.register(Category)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description",)
    search_fields = ("name",)

@admin.register(Product)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "brief_description", "description", "image",
                    "category", "price", "created_at", "updated_at",)
    list_filter = ("category", "price", "created_at", "updated_at",)
    search_fields = ("name", "brief_description", "category__name", "price", "created_at", "updated_at",)

@admin.register(Contacts)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "country", "address", "email",)
    search_fields = ("id", "email",)

@admin.register(MessageFeedback)
class MessageFeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "message", "created_at",)
    list_filter = ("name", "phone", "created_at",)
    search_fields = ("name", "phone",)
