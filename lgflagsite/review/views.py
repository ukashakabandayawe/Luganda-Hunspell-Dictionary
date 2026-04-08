from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .hunspell import generate_examples_for_flag, get_flag_description
from .models import Stem, StemFlagTask
from .services import update_working_dic_for_task_change


@login_required
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Log out the current user.

    We intentionally allow GET here to avoid CSRF errors that can happen when
    users switch accounts in multiple tabs (CSRF token rotation).
    """

    auth_logout(request)
    return redirect(getattr(settings, "LOGOUT_REDIRECT_URL", "/accounts/login/"))


@login_required
def my_queue(request):
    if request.user.is_staff:
        return redirect(reverse("admin:index"))
    stems = (
        Stem.objects.filter(assigned_to=request.user)
        .annotate(pending_count=Count("flag_tasks", filter=Q(flag_tasks__status=StemFlagTask.Status.PENDING)))
        .order_by("source_line_no", "id")
    )
    total_pending = stems.aggregate(total_pending=Sum("pending_count")).get("total_pending") or 0
    return render(request, "review/my_queue.html", {"stems": stems, "total_pending": total_pending})


@login_required
def review_stem(request, stem_id: int):
    if stem_id < 1:
        raise Http404()

    stem = get_object_or_404(Stem, id=stem_id)
    if not (request.user.is_staff or stem.assigned_to_id == request.user.id):
        raise Http404()

    tasks = StemFlagTask.objects.filter(stem=stem).select_related("flag")

    if request.method == "POST":
        task_id = request.POST.get("task_id")
        action = (request.POST.get("action") or "").lower().strip()
        note = (request.POST.get("note") or "").strip()

        task = get_object_or_404(StemFlagTask, id=task_id, stem=stem)
        prev = task.status
        if action == "approve":
            task.set_status(StemFlagTask.Status.APPROVED, request.user, note=note)
        elif action == "reject":
            task.set_status(StemFlagTask.Status.REJECTED, request.user, note=note)
        elif action == "skip":
            messages.error(request, "Skip is disabled. Please choose Approve or Reject.")
            return redirect("review:review_stem", stem_id=stem.id)
        else:
            messages.error(request, "Unknown action.")
            return redirect("review:review_stem", stem_id=stem.id)

        try:
            result = update_working_dic_for_task_change(
                task,
                prev,
                task.status,
                acting_user_id=request.user.id,
            )
            if not getattr(result, "did_sync", False):
                messages.success(request, "Decision saved. Working .dic will be rebuilt on download.")
            elif task.status == StemFlagTask.Status.APPROVED:
                messages.success(request, f"Approved. Updated {result.changed}/{result.matched} matching .dic lines.")
            elif prev == StemFlagTask.Status.APPROVED and task.status != StemFlagTask.Status.APPROVED:
                messages.success(request, "Decision saved. Working .dic rebuilt to reflect rollback.")
            else:
                messages.success(request, "Decision saved.")
        except Exception as ex:
            messages.error(request, f"Saved decision, but failed updating working .dic: {ex}")

        next_task = tasks.filter(status=StemFlagTask.Status.PENDING).order_by("flag__code").first()
        url = reverse("review:review_stem", kwargs={"stem_id": stem.id})
        if next_task is not None:
            url = f"{url}?task={next_task.id}"
        return redirect(url)

    # Pick which flag/task to show.
    task_param = (request.GET.get("task") or "").strip()
    current_task: StemFlagTask | None = None
    if task_param:
        try:
            tid = int(task_param)
        except ValueError:
            tid = 0
        if tid > 0:
            current_task = get_object_or_404(tasks, id=tid)

    if current_task is None:
        current_task = tasks.filter(status=StemFlagTask.Status.PENDING).order_by("flag__code").first()

    if current_task is None:
        current_task = tasks.order_by("flag__code").first()

    aff_path = Path(getattr(settings, "HUNSPELL_AFF_PATH"))

    task_rows = []
    if current_task is not None:
        code = current_task.flag.code
        desc = current_task.flag.description or get_flag_description(aff_path, code) or ""
        examples = generate_examples_for_flag(aff_path, code, stem.text, limit=120)
        task_rows.append(
            {
                "task": current_task,
                "code": code,
                "description": desc,
                "examples": examples,
            }
        )

    pending = tasks.filter(status=StemFlagTask.Status.PENDING).count()
    tasks_nav = list(tasks.order_by("flag__code").values("id", "flag__code", "status"))
    return render(
        request,
        "review/review_stem.html",
        {
            "stem": stem,
            "task_rows": task_rows,
            "pending": pending,
            "tasks_nav": tasks_nav,
        },
    )
