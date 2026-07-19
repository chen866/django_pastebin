from datetime import timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Clipboard, generate_short_id


def create_snippet(request):
    expiry_choices = [
        {"value": 1, "label": "1 小时"},
        {"value": 24, "label": "24 小时"},
        {"value": 24 * 7, "label": "7 天"},
        {"value": 24 * 31, "label": "1 个月"},
        {"value": 24 * (31 * 2), "label": "2 个月"},
        {"value": 24 * (30 * 3 + 2), "label": "3 个月"},
        {"value": 24 * (30 * 6 + 3), "label": "6 个月"},
        {"value": 24 * 365, "label": "1 年"},
        {"value": 24 * (365 * 2), "label": "2 年"},
    ]
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
                if not slug:
                    slug = generate_short_id()
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
                    return render(
                        request,
                        "clipboard/create.html",
                        {
                            "error": f"后缀已存在，请重新输入。{e!r}",
                            "form_data": request.POST,
                            "expiry_choices": expiry_choices,
                        },
                    )
                if i == MAX_RETRY_COUNT - 1:
                    # 如果尝试了10次，仍然无法创建，则抛出异常
                    return render(
                        request,
                        "clipboard/create.html",
                        {
                            "error": f"后缀无法创建，请重新输入。{e!r}",
                            "form_data": request.POST,
                            "expiry_choices": expiry_choices,
                        },
                    )
                continue
        else:
            return render(
                request,
                "clipboard/create.html",
                {"error": "无法创建，请重新重试。", "form_data": request.POST, "expiry_choices": expiry_choices},
            )

        return redirect("view_snippet", slug=snippet.slug)

    return render(request, "clipboard/create.html", {"expiry_choices": expiry_choices})


def view_snippet(request, slug):
    snippet = Clipboard.objects.filter(slug=slug).first()
    if not snippet:
        return render(
            request, "422.html", {"error_title": f"该内容不存在：{slug}", "error_message": f"该内容不存在：{slug}"}
        )

    if snippet.is_expired():
        snippet.delete()
        return render(
            request, "422.html", {"error_title": f"该内容已过期：{slug}", "error_message": f"该内容已过期：{slug}"}
        )

    return render(request, "clipboard/view.html", {"snippet": snippet})


@login_required(login_url="/admin/login/")
@permission_required("clipboard.view_clipboard", login_url="/admin/login/")
def list_snippets(request):
    snippets = Clipboard.objects.all().order_by("-created_at")[:100]
    return render(request, "clipboard/list.html", {"snippets": snippets})
