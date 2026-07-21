from django.contrib import admin

from .models import Clipboard, Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("content_type", "object_id", "user", "short_content", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("content", "user__username")
    list_per_page = 100
    list_max_show_all = 100
    list_display_links = ("content_type", "object_id")

    @admin.display(description="Content", ordering="content")
    def short_content(self, obj):
        if len(obj.content) > 1000:
            return obj.content[:1000] + "..."
        return obj.content


@admin.register(Clipboard)
class ClipboardAdmin(admin.ModelAdmin):
    list_display = ("slug", "short_content", "format_type", "created_at", "expires_at")
    list_filter = ("format_type", "created_at", "expires_at")
    search_fields = ("slug", "content")
    list_per_page = 100
    list_max_show_all = 100
    list_display_links = ("slug",)

    @admin.display(description="Content", ordering="content")
    def short_content(self, obj):
        if len(obj.content) > 1000:
            return obj.content[:1000] + "..."
        return obj.content
