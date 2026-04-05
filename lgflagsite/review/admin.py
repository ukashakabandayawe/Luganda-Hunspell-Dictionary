from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import FileResponse
from django.template.response import TemplateResponse
from django.utils import timezone

from .dic_io import ensure_working_dic_exists
from .models import Flag, ReviewDecision, Stem, StemFlagTask
from .services import rebuild_working_dic_for_user_id, working_dic_path_for_user_id


def _safe_filename_part(value: str) -> str:
	value = (value or "").strip()
	return "".join(ch for ch in value if ch.isalnum() or ch in ("-", "_", ".")) or "user"


@admin.action(description="Download user's working Luganda.dic")
def download_user_working_dic(modeladmin, request, queryset):
	if queryset.count() != 1:
		modeladmin.message_user(request, "Select exactly 1 user to download their working .dic.", level=messages.WARNING)
		return None

	user = queryset.first()
	if user is None:
		modeladmin.message_user(request, "User not found.", level=messages.ERROR)
		return None

	source_dic = Path(getattr(settings, "HUNSPELL_DIC_SOURCE_PATH"))
	working_dic = working_dic_path_for_user_id(int(user.id))

	# On ephemeral hosts, the working file may be missing after redeploy.
	# Rebuild from DB approvals so downloads always reflect review progress.
	if not working_dic.exists():
		rebuild_working_dic_for_user_id(int(user.id))
	else:
		ensure_working_dic_exists(source_dic, working_dic)
	if not working_dic.exists():
		modeladmin.message_user(request, f"Working .dic not found: {working_dic}", level=messages.ERROR)
		return None

	filename = f"Luganda_{_safe_filename_part(getattr(user, 'username', '') or str(user.id))}.dic"
	return FileResponse(open(working_dic, "rb"), as_attachment=True, filename=filename)


class UserAdminWithWorkingDic(DjangoUserAdmin):
	actions = (download_user_working_dic,)


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
	list_display = ("code", "affix_type", "group", "is_active")
	list_filter = ("affix_type", "group", "is_active")
	search_fields = ("code", "description")
	ordering = ("aff_order", "code")
	actions = (
		"mark_selected_flags_priority",
		"mark_selected_flags_nouns",
		"mark_selected_flags_adjectives",
		"mark_selected_flags_reflexive_verbs",
		"set_selected_flags_group",
	)

	@admin.action(description="Mark selected flags as Priority")
	def mark_selected_flags_priority(self, request, queryset):
		updated = queryset.update(group=Flag.Group.PRIORITY)
		self.message_user(request, f"Updated {updated} flags to group '{Flag.Group.PRIORITY.label}'.", level=messages.SUCCESS)

	@admin.action(description="Mark selected flags as Nouns")
	def mark_selected_flags_nouns(self, request, queryset):
		updated = queryset.update(group=Flag.Group.NOUNS)
		self.message_user(request, f"Updated {updated} flags to group '{Flag.Group.NOUNS.label}'.", level=messages.SUCCESS)

	@admin.action(description="Mark selected flags as Adjectives")
	def mark_selected_flags_adjectives(self, request, queryset):
		updated = queryset.update(group=Flag.Group.ADJECTIVES)
		self.message_user(request, f"Updated {updated} flags to group '{Flag.Group.ADJECTIVES.label}'.", level=messages.SUCCESS)

	@admin.action(description="Mark selected flags as Reflexive verbs")
	def mark_selected_flags_reflexive_verbs(self, request, queryset):
		updated = queryset.update(group=Flag.Group.REFLEXIVE_VERBS)
		self.message_user(
			request,
			f"Updated {updated} flags to group '{Flag.Group.REFLEXIVE_VERBS.label}'.",
			level=messages.SUCCESS,
		)

	@admin.action(description="Set group for selected flags")
	def set_selected_flags_group(self, request, queryset):
		if "apply" in request.POST:
			group = (request.POST.get("flag_group") or "").strip()
			allowed_groups = {c[0] for c in Flag.Group.choices}
			if group not in allowed_groups:
				self.message_user(request, "Select a valid flag group.", level=messages.ERROR)
				return None

			updated = queryset.update(group=group)
			self.message_user(
				request,
				f"Updated {updated} flags to group '{Flag.Group(group).label}'.",
				level=messages.SUCCESS,
			)
			return None

		request.current_app = self.admin_site.name
		context = {
			**self.admin_site.each_context(request),
			"title": "Set group for flags",
			"flags": queryset,
			"flag_groups": list(Flag.Group.choices),
			"current_flag_group": "",
			"action_name": "set_selected_flags_group",
			"opts": self.model._meta,
		}
		return TemplateResponse(request, "admin/review_set_flag_group.html", context)


@admin.register(Stem)
class StemAdmin(admin.ModelAdmin):
	list_display = ("text", "flags_raw", "assigned_to", "assigned_at", "source_line_no")
	list_filter = ("assigned_to",)
	search_fields = ("text", "flags_raw")
	ordering = ("source_line_no", "text")
	actions = (
		"assign_selected_to_user",
		"unassign_selected",
		"create_flag_tasks_for_selected",
		"ensure_all_flag_tasks_for_selected",
	)

	@admin.action(description="Ensure review tasks for ALL active flags")
	def ensure_all_flag_tasks_for_selected(self, request, queryset):
		stem_ids = list(queryset.values_list("id", flat=True))
		flags = list(Flag.objects.filter(is_active=True).values_list("id", flat=True))
		if not stem_ids:
			self.message_user(request, "No stems selected.", level=messages.WARNING)
			return
		if not flags:
			self.message_user(request, "No active flags found.", level=messages.ERROR)
			return

		batch: list[StemFlagTask] = []
		batch_size = 5000
		for sid in stem_ids:
			for fid in flags:
				batch.append(StemFlagTask(stem_id=sid, flag_id=fid))
				if len(batch) >= batch_size:
					StemFlagTask.objects.bulk_create(batch, ignore_conflicts=True)
					batch.clear()
		if batch:
			StemFlagTask.objects.bulk_create(batch, ignore_conflicts=True)

		self.message_user(
			request,
			f"Ensured review tasks for {len(stem_ids)} stems × {len(flags)} active flags.",
			level=messages.SUCCESS,
		)

	@admin.action(description="Assign selected stems to a user")
	def assign_selected_to_user(self, request, queryset):
		if "apply" in request.POST:
			user_id = request.POST.get("user_id")
			group = (request.POST.get("flag_group") or Flag.Group.PRIORITY).strip()
			allowed_groups = {c[0] for c in Flag.Group.choices}
			if group not in allowed_groups:
				self.message_user(request, "Invalid flag group.", level=messages.ERROR)
				return None
			if not user_id:
				self.message_user(request, "Select a user.", level=messages.ERROR)
				return None
			User = get_user_model()
			try:
				user = User.objects.get(id=user_id)
			except User.DoesNotExist:
				self.message_user(request, "User not found.", level=messages.ERROR)
				return None

			stem_ids = list(queryset.values_list("id", flat=True))
			count = len(stem_ids)
			flags = list(Flag.objects.filter(is_active=True, group=group).values_list("id", flat=True))
			if stem_ids and not flags:
				self.message_user(
					request,
					f"No active flags found in group '{Flag.Group(group).label}'.",
					level=messages.ERROR,
				)
				return None
			now = timezone.now()
			Stem.objects.filter(id__in=stem_ids).update(assigned_to=user, assigned_at=now)

			if stem_ids and flags:
				batch: list[StemFlagTask] = []
				batch_size = 5000
				for sid in stem_ids:
					for fid in flags:
						batch.append(StemFlagTask(stem_id=sid, flag_id=fid))
						if len(batch) >= batch_size:
							StemFlagTask.objects.bulk_create(batch, ignore_conflicts=True)
							batch.clear()
				if batch:
					StemFlagTask.objects.bulk_create(batch, ignore_conflicts=True)

			self.message_user(
				request,
				f"Assigned {count} stems to {user.username}. Review tasks ensured for {len(flags)} active flags in group '{Flag.Group(group).label}'.",
				level=messages.SUCCESS,
			)
			return None

		users = get_user_model().objects.filter(is_active=True).order_by("username")
		request.current_app = self.admin_site.name
		context = {
			**self.admin_site.each_context(request),
			"title": "Assign stems",
			"stems": queryset,
			"users": users,
			"flag_groups": list(Flag.Group.choices),
			"current_flag_group": Flag.Group.PRIORITY,
			"action_name": "assign_selected_to_user",
			"opts": self.model._meta,
		}
		return TemplateResponse(request, "admin/review_assign_stems.html", context)

	@admin.action(description="Unassign selected stems")
	def unassign_selected(self, request, queryset):
		count = queryset.count()
		queryset.update(assigned_to=None, assigned_at=None)
		self.message_user(request, f"Unassigned {count} stems.", level=messages.SUCCESS)

	@admin.action(description="Create review tasks (stem+flag) for selected stems")
	def create_flag_tasks_for_selected(self, request, queryset):
		if "apply" in request.POST:
			flag_ids = request.POST.getlist("flag_ids")
			if not flag_ids:
				self.message_user(request, "Select one or more flags.", level=messages.ERROR)
				return None

			flags = list(Flag.objects.filter(id__in=flag_ids, is_active=True).order_by("code"))
			if not flags:
				self.message_user(request, "No valid active flags selected.", level=messages.ERROR)
				return None

			created = 0
			for stem in queryset:
				for flag in flags:
					_, is_new = StemFlagTask.objects.get_or_create(stem=stem, flag=flag)
					if is_new:
						created += 1
			self.message_user(request, f"Created {created} tasks.", level=messages.SUCCESS)
			return None

		flags = Flag.objects.filter(is_active=True).order_by("code")
		request.current_app = self.admin_site.name
		context = {
			**self.admin_site.each_context(request),
			"title": "Create tasks for stems",
			"stems": queryset,
			"flags": flags,
			"action_name": "create_flag_tasks_for_selected",
			"opts": self.model._meta,
		}
		return TemplateResponse(request, "admin/review_create_tasks.html", context)


@admin.register(StemFlagTask)
class StemFlagTaskAdmin(admin.ModelAdmin):
	list_display = ("stem", "flag", "status", "decided_by", "decided_at", "updated_at")
	list_filter = ("status", "flag", "decided_by")
	search_fields = ("stem__text", "flag__code")


@admin.register(ReviewDecision)
class ReviewDecisionAdmin(admin.ModelAdmin):
	list_display = ("created_at", "user", "task", "decision")
	list_filter = ("decision", "user")
	search_fields = ("task__stem__text", "task__flag__code", "note")
	ordering = ("-created_at",)


# Re-register the User model with our extra admin action.
try:
	User = get_user_model()
	try:
		admin.site.unregister(User)
	except admin.sites.NotRegistered:
		pass
	admin.site.register(User, UserAdminWithWorkingDic)
except Exception:
	# Best-effort only; never break admin due to registration issues.
	pass
