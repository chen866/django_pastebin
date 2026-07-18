from datetime import timedelta

from django.db import IntegrityError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Clipboard


def create_snippet(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        slug = request.POST.get("slug", "").strip()
        format_type = request.POST.get("format_type", "text")
        expiry_hours = int(request.POST.get("expiry", 24))

        if not content:
            return render(request, "clipboard/create.html", {"error": "内容不能为空"})

        if not slug:
            slug = None

        expires_at = timezone.now() + timedelta(hours=expiry_hours)

        while True:  # 如果slug已经存在，则重新生成一个
            try:
                snippet = Clipboard.objects.create(
                    slug=slug,
                    format_type=format_type,
                    content=content,
                    expires_at=expires_at,
                )
                break
            except IntegrityError:
                continue

        return redirect("view_snippet", slug=snippet.slug)

    return render(request, "clipboard/create.html")


def view_snippet(request, slug):
    snippet = get_object_or_404(Clipboard, slug=slug)

    if snippet.is_expired():
        snippet.delete()
        raise Http404("该内容已过期并被永久销毁。")

    return render(request, "clipboard/view.html", {"snippet": snippet})
