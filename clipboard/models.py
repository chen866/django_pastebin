import random
import string

from django.db import models
from django.utils import timezone


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

    class Meta:
        db_table = "clipboard_data"

    def is_expired(self):
        return self.expires_at and timezone.now() > self.expires_at
