from datetime import timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Clipboard, Comment, generate_short_id


def error_422(request, title, message):
    return render(request, "422.html", {"error_title": title, "error_message": message})


def create_snippet(request):
    EXPIRY_CHOICES = [
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

        def _render_create_error(request, error_message, form_data=None):
            return render(
                request,
                "clipboard/create.html",
                {
                    "error": error_message,
                    "form_data": form_data or request.POST,
                    "expiry_choices": EXPIRY_CHOICES,
                },
            )

        if not content:
            return _render_create_error(request, "内容不能为空")

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
                    return _render_create_error(request, f"后缀已存在，请重新输入。{e!r}")
                if i == MAX_RETRY_COUNT - 1:
                    return _render_create_error(request, f"后缀无法创建，请重新输入。{e!r}")
                continue
        else:
            return _render_create_error(request, "无法创建，请重新重试。")

        return redirect("view_snippet", slug=snippet.slug)

    # 未提交表单，则渲染创建页面
    return render(request, "clipboard/create.html", {"expiry_choices": EXPIRY_CHOICES})


def view_snippet(request, slug):
    snippet = Clipboard.objects.filter(slug=slug).first()
    if not snippet:
        return error_422(request, f"该内容不存在：{slug}", f"该内容不存在：{slug}")

    if snippet.is_expired():
        snippet.delete()
        return error_422(request, f"该内容已过期：{slug}", f"该内容已过期：{slug}")

    return render(request, "clipboard/view.html", {"snippet": snippet})


@login_required(login_url="/admin/login/")
@permission_required("clipboard.view_clipboard", login_url="/admin/login/")
def list_snippets(request):
    snippets = Clipboard.objects.all().order_by("-created_at")[:100]
    has_delete_permission = request.user.has_perm("clipboard.delete_clipboard")
    return render(
        request, "clipboard/list.html", {"snippets": snippets, "has_delete_permission": has_delete_permission}
    )


@login_required(login_url="/admin/login/")
@permission_required("clipboard.delete_clipboard", login_url="/admin/login/")
def delete_snippet(request, slug):
    snippet = Clipboard.objects.filter(slug=slug).first()
    if snippet:
        snippet.delete()
    return redirect("list_snippets")


@require_http_methods(["GET"])
def list_comments(request, slug):
    clipboard = get_object_or_404(Clipboard, slug=slug)
    if clipboard.is_expired():
        return JsonResponse({"error": "This snippet has expired"}, status=410)
    
    comments = clipboard.comments.all()
    data = [
        {
            "id": c.id,
            "user": c.user.username,
            "content": c.content,
            "created_at": c.created_at.isoformat(),
        }
        for c in comments
    ]
    return JsonResponse({"comments": data})


@login_required
@require_http_methods(["POST"])
def post_comment(request, slug):
    clipboard = get_object_or_404(Clipboard, slug=slug)
    if clipboard.is_expired():
        return JsonResponse({"error": "This snippet has expired"}, status=410)
    
    content = request.POST.get("content", "").strip()
    if not content:
        return JsonResponse({"error": "Comment cannot be empty"}, status=400)
    
    comment = Comment.objects.create(
        content_object=clipboard,
        user=request.user,
        content=content,
    )
    return JsonResponse(
        {
            "id": comment.id,
            "user": comment.user.username,
            "content": comment.content,
            "created_at": comment.created_at.isoformat(),
        },
        status=201,
    )
