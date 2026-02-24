from django.contrib import admin
from .models import Category, Product, Contacts, MessageFeedback


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "brief_description", "description", "image",
                    "category", "price", "created_at", "updated_at", "status")
    list_editable = ("status", "category")
    list_filter = ("category", "owner", "price", "created_at", "updated_at", "status")
    search_fields = ("name", "brief_description", "price")


@admin.register(Contacts)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "country", "address", "email",)
    search_fields = ("id", "email",)


@admin.register(MessageFeedback)
class MessageFeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "message", "created_at",)
    list_filter = ("name", "email", "created_at",)
    search_fields = ("name", "email",)
