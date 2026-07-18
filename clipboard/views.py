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

        slug_manual = True
        if not slug:
            slug = None
            slug_manual = False

        expires_at = timezone.now() + timedelta(hours=expiry_hours)

        MAX_RETRY_COUNT = 5
        for i in range(MAX_RETRY_COUNT):
            try:
                snippet = Clipboard.objects.create(
                    slug=slug,
                    format_type=format_type,
                    content=content,
                    expires_at=expires_at,
                )
                break
            except IntegrityError as e:
                if slug_manual:
                    # 手动指定后缀时，如果slug已经存在，则抛出异常
                    return render(request, "clipboard/create.html", {"error": f"后缀已存在，请重新输入。{e!r}"})
                if i == MAX_RETRY_COUNT - 1:
                    # 如果尝试了10次，仍然无法创建，则抛出异常
                    return render(request, "clipboard/create.html", {"error": f"后缀无法创建，请重新输入。{e!r}"})
                continue
        else:
            return render(request, "clipboard/create.html", {"error": "无法创建，请重新重试。"})

        return redirect("view_snippet", slug=snippet.slug)

    return render(request, "clipboard/create.html")


def view_snippet(request, slug):
    snippet = get_object_or_404(Clipboard, slug=slug)

    if snippet.is_expired():
        snippet.delete()
        raise Http404("该内容已过期并被永久销毁。")

    return render(request, "clipboard/view.html", {"snippet": snippet})
