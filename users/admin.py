from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username", "date_joined", "last_login", "is_superuser", "is_staff",
                    "is_active", "country", "is_mailing_recipient")
    list_filter = ("date_joined", "last_login", "is_superuser", "is_staff", "is_active", "groups",
                   "is_mailing_recipient")
    search_fields = ("email", "username", "id",)
