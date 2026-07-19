import random
import string

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="clipboard_comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"


def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


class Clipboard(models.Model):
    FORMAT_CHOICES = (
        ("text", "纯文本"),
        ("markdown", "Markdown"),
    )

    slug = models.CharField(max_length=10, unique=True, default=generate_short_id, db_index=True)
    content = models.TextField()
    format_type = models.CharField(max_length=10, choices=FORMAT_CHOICES, default="text")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    comments = GenericRelation("Comment")

    class Meta:
        db_table = "clipboard_data"

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at
