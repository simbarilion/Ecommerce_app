from django.contrib import admin
from .models import Blogpost


@admin.register(Blogpost)
class BlogpostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at",
                    "updated_at", "status", "number_of_views",)
    list_editable = ("status",)
    list_filter = ("author", "created_at", "updated_at", "status", "number_of_views")
    search_fields = ("id", "title",)
