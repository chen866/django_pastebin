from django.contrib import admin
from .models import Clipboard   

@admin.register(Clipboard)
class ClipboardAdmin(admin.ModelAdmin):
    list_display = ("slug", "content", "format_type", "created_at", "expires_at")
    list_filter = ("format_type", "created_at", "expires_at")
    search_fields = ("slug", "content")
    list_per_page = 100
    list_max_show_all = 100
    list_display_links = ("slug",)