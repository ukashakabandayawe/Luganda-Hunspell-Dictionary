from pathlib import Path

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import FileResponse
from django.db.models import Count, Max, Min, Q
from django.template.response import TemplateResponse
from django.utils import timezone

from .dic_io import ensure_working_dic_exists
from .models import Flag, ReviewDecision, Stem, StemFlagTask
from .models import StemGroup
from .offline_bundle import build_offline_review_bundle_payload
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
	if not getattr(settings, "WORKING_DIC_SYNC_ON_REVIEW", True):
		rebuild_working_dic_for_user_id(int(user.id))
	elif not working_dic.exists():
		rebuild_working_dic_for_user_id(int(user.id))
	else:
		ensure_working_dic_exists(source_dic, working_dic)
	if not working_dic.exists():
		modeladmin.message_user(request, f"Working .dic not found: {working_dic}", level=messages.ERROR)
		return None

	filename = f"Luganda_{_safe_filename_part(getattr(user, 'username', '') or str(user.id))}.dic"
	return FileResponse(open(working_dic, "rb"), as_attachment=True, filename=filename)


@admin.action(description="Download user's offline review bundle (.json.gz)")
def download_user_offline_review_bundle(modeladmin, request, queryset):
	if queryset.count() != 1:
		modeladmin.message_user(request, "Select exactly 1 user to export a bundle for.", level=messages.WARNING)
		return None

	user = queryset.first()
	if user is None:
		modeladmin.message_user(request, "User not found.", level=messages.ERROR)
		return None

	if "apply" in request.POST:
		limit_raw = (request.POST.get("limit_examples") or "120").strip()
		examples_for = (request.POST.get("examples_for") or "pending").strip().lower()
		try:
			limit_examples = int(limit_raw)
		except ValueError:
			modeladmin.message_user(request, "Limit examples must be a number.", level=messages.ERROR)
			return None
		if limit_examples < 0:
			modeladmin.message_user(request, "Limit examples must be >= 0.", level=messages.ERROR)
			return None
		if examples_for not in {"pending", "all"}:
			modeladmin.message_user(request, "Examples for must be 'pending' or 'all'.", level=messages.ERROR)
			return None

		try:
			payload = build_offline_review_bundle_payload(
				user=user,
				limit_examples=limit_examples,
				examples_for=examples_for,
			)
			# Write to disk first so FileResponse can stream efficiently (and include Content-Length).
			data_dir = Path(getattr(settings, "DATA_DIR"))
			out_path = (data_dir / "bundles" / f"bundle_{getattr(user, 'username', str(user.id))}.json.gz").resolve()
			out_path.parent.mkdir(parents=True, exist_ok=True)
			import gzip
			import json

			with gzip.open(out_path, "wt", compresslevel=9, encoding="utf-8") as f:
				json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
		except Exception as ex:
			modeladmin.message_user(request, f"Failed to export bundle: {ex}", level=messages.ERROR)
			return None

		filename = f"bundle_{_safe_filename_part(getattr(user, 'username', '') or str(user.id))}.json.gz"
		return FileResponse(open(out_path, "rb"), as_attachment=True, filename=filename, content_type="application/gzip")

	request.current_app = modeladmin.admin_site.name
	context = {
		**modeladmin.admin_site.each_context(request),
		"title": "Export offline review bundle",
		"users": queryset,
		"action_name": "download_user_offline_review_bundle",
		"current_limit_examples": 0,
		"current_examples_for": "pending",
		"opts": queryset.model._meta,
	}
	return TemplateResponse(request, "admin/review_export_bundle.html", context)


class UserAdminWithWorkingDic(DjangoUserAdmin):
	list_display = (
		"username",
		"assigned_stems_count",
		"assigned_stem_groups_count",
		"email",
		"first_name",
		"last_name",
		"is_staff",
	)
	actions = (download_user_working_dic, download_user_offline_review_bundle)

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		return qs.annotate(
			_assigned_stems=Count("assigned_stems", distinct=True),
			_assigned_stem_groups=Count(
				"assigned_stems__group",
				filter=Q(assigned_stems__group__isnull=False),
				distinct=True,
			),
		)

	@admin.display(description="# stems", ordering="_assigned_stems")
	def assigned_stems_count(self, obj) -> int:
		try:
			return int(getattr(obj, "_assigned_stems", 0) or 0)
		except Exception:
			return 0

	@admin.display(description="# stem groups", ordering="_assigned_stem_groups")
	def assigned_stem_groups_count(self, obj) -> int:
		try:
			return int(getattr(obj, "_assigned_stem_groups", 0) or 0)
		except Exception:
			return 0


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
	list_display = ("code", "affix_type", "group", "is_active")
	list_filter = ("affix_type", "group", "is_active")
	search_fields = ("code", "description", "aff_description")
	ordering = ("aff_order", "code")
	fieldsets = (
		(
			None,
			{
				"fields": (
					"code",
					"affix_type",
					"group",
					"is_active",
					"aff_order",
				),
			},
		),
		(
			"Reviewer description (editable)",
			{
				"fields": ("description",),
				"description": "This is what reviewers will see in the Android app and the Django review page.",
			},
		),
		(
			"From Luganda.aff (auto-synced)",
			{
				"fields": ("aff_description",),
				"description": "Developer-oriented description parsed from Luganda.aff comments. Used only when the reviewer description is blank.",
			},
		),
	)
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
	list_display = ("text", "group_title", "flags_raw", "assigned_to", "assigned_at", "source_line_no")
	list_filter = ("assigned_to", "group")
	search_fields = ("text", "flags_raw")
	ordering = ("source_line_no", "text")
	actions = (
		"assign_selected_to_user",
		"unassign_selected",
		"create_flag_tasks_for_selected",
		"ensure_all_flag_tasks_for_selected",
		"set_flag_groups_for_selected_stem_groups",
	)

	@admin.action(description="Set flag group(s) for selected stems' stem group(s)")
	def set_flag_groups_for_selected_stem_groups(self, request, queryset):
		if "apply" in request.POST:
			allowed_groups = {c[0] for c in Flag.Group.choices}
			groups = [g.strip() for g in request.POST.getlist("flag_groups") if (g or "").strip()]
			if not groups:
				self.message_user(request, "Select one or more flag groups.", level=messages.ERROR)
				return None
			invalid = [g for g in groups if g not in allowed_groups]
			if invalid:
				self.message_user(request, f"Invalid flag group(s): {', '.join(invalid)}.", level=messages.ERROR)
				return None

			stem_ids = list(queryset.values_list("id", flat=True))
			group_ids = list(
				Stem.objects.filter(id__in=stem_ids)
				.exclude(group_id__isnull=True)
				.values_list("group_id", flat=True)
				.distinct()
			)
			if not group_ids:
				self.message_user(request, "No selected stems belong to a stem group.", level=messages.WARNING)
				return None

			# Normalize (dedupe + stable order).
			uniq = []
			seen = set()
			for g in groups:
				if g in seen:
					continue
				seen.add(g)
				uniq.append(g)

			updated = 0
			for sg in StemGroup.objects.filter(id__in=group_ids):
				sg.flag_groups = list(uniq)
				sg.save(update_fields=["flag_groups"])
				updated += 1

			labels = ", ".join(Flag.Group(g).label for g in uniq)
			self.message_user(
				request,
				f"Set flag group(s) for {updated} stem groups: {labels}.",
				level=messages.SUCCESS,
			)
			return None

		# Preview the stem groups affected.
		stem_ids = list(queryset.values_list("id", flat=True))
		groups = list(
			StemGroup.objects.filter(
				id__in=(
					Stem.objects.filter(id__in=stem_ids)
					.exclude(group_id__isnull=True)
					.values_list("group_id", flat=True)
					.distinct()
				)
			).order_by("source_line_no", "title")
		)
		request.current_app = self.admin_site.name
		context = {
			**self.admin_site.each_context(request),
			"title": "Set flag group(s) for stem groups",
			"stem_groups": groups,
			"stems": queryset,
			"flag_groups": list(Flag.Group.choices),
			"current_flag_groups": [],
			"action_name": "set_flag_groups_for_selected_stem_groups",
			"opts": self.model._meta,
		}
		return TemplateResponse(request, "admin/review_set_stem_group_flag_groups.html", context)

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

	@admin.display(description="Group")
	def group_title(self, obj: Stem):
		try:
			g = getattr(obj, "group", None)
			return g.title if g else ""
		except Exception:
			return ""

	def _expand_stems_by_group(self, queryset):
		# If any selected stems are in a group, include the full group.
		qs = queryset.select_related("group")
		group_ids = list(qs.exclude(group_id__isnull=True).values_list("group_id", flat=True).distinct())
		stem_ids = set(qs.values_list("id", flat=True))
		if group_ids:
			stem_ids.update(Stem.objects.filter(group_id__in=group_ids).values_list("id", flat=True))
		return Stem.objects.filter(id__in=stem_ids).select_related("group")

	def _grouped_preview_rows(self, stems):
		# Build accordion-friendly groups.
		rows = []
		stems = list(stems)
		# Sort so group blocks follow file order.
		def sort_key(s: Stem):
			g = getattr(s, "group", None)
			g_line = getattr(g, "source_line_no", 10**9) if g else 10**9
			return (g_line, int(s.source_line_no or 0), s.text)
		stems.sort(key=sort_key)

		buckets = {}
		order = []
		for s in stems:
			g = getattr(s, "group", None)
			if g is not None:
				key = ("group", int(g.id))
				title = g.title
				line = int(getattr(g, "source_line_no", 0) or 0)
			else:
				key = ("stem", int(s.id))
				title = s.text
				line = int(s.source_line_no or 0)
			if key not in buckets:
				buckets[key] = {"title": title, "source_line_no": line, "stems": []}
				order.append(key)
			buckets[key]["stems"].append(s)

		for key in order:
			rows.append(buckets[key])
		return rows

	@admin.action(description="Assign selected stems to a user")
	def assign_selected_to_user(self, request, queryset):
		queryset = self._expand_stems_by_group(queryset)
		if "apply" in request.POST:
			user_id = request.POST.get("user_id")
			allowed_groups = {c[0] for c in Flag.Group.choices}
			# New UI posts multiple values under flag_groups[]. Keep backward compatibility
			# with the old single-select name (flag_group).
			groups = [g.strip() for g in request.POST.getlist("flag_groups") if (g or "").strip()]
			if not groups:
				fallback = (request.POST.get("flag_group") or "").strip()
				if fallback:
					groups = [fallback]
			if not groups:
				self.message_user(request, "Select one or more flag groups.", level=messages.ERROR)
				return None
			invalid = [g for g in groups if g not in allowed_groups]
			if invalid:
				self.message_user(request, f"Invalid flag group(s): {', '.join(invalid)}.", level=messages.ERROR)
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
			flags = list(Flag.objects.filter(is_active=True, group__in=groups).values_list("id", flat=True))
			if stem_ids and not flags:
				labels = ", ".join(Flag.Group(g).label for g in groups)
				self.message_user(
					request,
					f"No active flags found in selected group(s): {labels}.",
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

			labels = ", ".join(Flag.Group(g).label for g in groups)
			self.message_user(
				request,
				f"Assigned {count} stems to {user.username}. Review tasks ensured for {len(flags)} active flags in group(s): {labels}.",
				level=messages.SUCCESS,
			)
			return None

		users = get_user_model().objects.filter(is_active=True).order_by("username")
		request.current_app = self.admin_site.name
		grouped_stems = self._grouped_preview_rows(queryset)
		context = {
			**self.admin_site.each_context(request),
			"title": "Assign stems",
			"stems": queryset,
			"grouped_stems": grouped_stems,
			"users": users,
			"flag_groups": list(Flag.Group.choices),
			"current_flag_groups": [Flag.Group.PRIORITY],
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


@admin.register(StemGroup)
class StemGroupAdmin(admin.ModelAdmin):
	list_display = ("title", "assigned_to", "flag_groups_display", "stems_count", "source_line_no")
	search_fields = ("title",)
	ordering = ("source_line_no", "title")
	actions = (
		"assign_selected_groups_to_user",
		"unassign_selected_groups",
		"set_flag_groups_for_selected_groups",
	)

	def get_actions(self, request):
		actions = super().get_actions(request)
		User = get_user_model()
		# Keep the actions menu usable; if you have a lot of users,
		# fall back to the generic "Assign ... to a user" action.
		reviewers = list(
			User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
			.only("id", "username")
			.order_by("username")
		)
		max_dynamic = 40
		if len(reviewers) > max_dynamic:
			return actions

		for u in reviewers:
			uid = int(u.id)
			username = (getattr(u, "username", "") or str(uid)).strip()
			label = username[:1].upper() + username[1:]
			action_name = f"assign_selected_stem_groups_to_user_{uid}"

			def _make_action(target_user_id: int, target_label: str):
				def _action(modeladmin, req, queryset):
					return modeladmin._assign_selected_groups_to_specific_user(req, queryset, target_user_id)
				_action.__name__ = f"assign_selected_stem_groups_to_user_{target_user_id}"
				_action.short_description = f"Assign selected stem groups to {target_label}"
				return _action

			actions[action_name] = (
				_make_action(uid, label),
				action_name,
				f"Assign selected stem groups to {label}",
			)
		return actions

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		return qs.annotate(
			_total_stems=Count("stems", distinct=True),
			_unassigned_stems=Count(
				"stems",
				filter=Q(stems__assigned_to__isnull=True),
				distinct=True,
			),
			_assignee_min=Min("stems__assigned_to__username"),
			_assignee_max=Max("stems__assigned_to__username"),
		)

	@admin.display(description="# stems")
	def stems_count(self, obj: StemGroup) -> int:
		try:
			return obj.stems.count()
		except Exception:
			return 0

	@admin.display(description="Assigned to", ordering="_assignee_min")
	def assigned_to(self, obj: StemGroup) -> str:
		total = getattr(obj, "_total_stems", None)
		unassigned = getattr(obj, "_unassigned_stems", None)
		assignee_min = getattr(obj, "_assignee_min", None)
		assignee_max = getattr(obj, "_assignee_max", None)
		# Fallback for safety if queryset isn't annotated.
		if total is None or unassigned is None:
			assigned_usernames = list(
				obj.stems.exclude(assigned_to__isnull=True).values_list("assigned_to__username", flat=True).distinct()
			)
			if not assigned_usernames:
				return "Unassigned"
			if len(assigned_usernames) == 1 and obj.stems.filter(assigned_to__isnull=True).count() == 0:
				return assigned_usernames[0]
			return "Mixed"

		if total == 0:
			return "Unassigned"
		if unassigned == total:
			return "Unassigned"
		if unassigned and unassigned > 0:
			return "Mixed"
		if assignee_min and assignee_min == assignee_max:
			return str(assignee_min)
		return "Mixed"

	@admin.display(description="Flag group(s)")
	def flag_groups_display(self, obj: StemGroup) -> str:
		try:
			groups = list(getattr(obj, "flag_groups", None) or [])
		except Exception:
			groups = []
		allowed = {c[0] for c in Flag.Group.choices}
		labels = []
		for g in groups:
			if g not in allowed:
				continue
			labels.append(Flag.Group(g).label)
		return ", ".join(labels)

	@admin.action(description="Assign selected stem groups to a user")
	def assign_selected_groups_to_user(self, request, queryset):
		if "apply" in request.POST:
			user_id = request.POST.get("user_id")
			allowed_groups = {c[0] for c in Flag.Group.choices}
			groups = [g.strip() for g in request.POST.getlist("flag_groups") if (g or "").strip()]
			if not groups:
				fallback = (request.POST.get("flag_group") or "").strip()
				if fallback:
					groups = [fallback]
			# If nothing was selected, default to the union of the selected stem groups'
			# stored flag group(s). This makes assignment a one-step action once groups
			# are classified.
			if not groups:
				union: list[str] = []
				seen = set()
				for sg in queryset:
					for g in (getattr(sg, "flag_groups", None) or []):
						g = (g or "").strip()
						if not g or g in seen:
							continue
						seen.add(g)
						union.append(g)
				groups = union
			if not groups:
				self.message_user(
					request,
					"Select one or more flag groups (or set flag groups on these stem groups first).",
					level=messages.ERROR,
				)
				return None
			invalid = [g for g in groups if g not in allowed_groups]
			if invalid:
				self.message_user(request, f"Invalid flag group(s): {', '.join(invalid)}.", level=messages.ERROR)
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

			group_ids = list(queryset.values_list("id", flat=True))
			stem_ids = list(Stem.objects.filter(group_id__in=group_ids).values_list("id", flat=True))
			count = len(stem_ids)
			flags = list(Flag.objects.filter(is_active=True, group__in=groups).values_list("id", flat=True))
			if stem_ids and not flags:
				labels = ", ".join(Flag.Group(g).label for g in groups)
				self.message_user(
					request,
					f"No active flags found in selected group(s): {labels}.",
					level=messages.ERROR,
				)
				return None

			now = timezone.now()
			if stem_ids:
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

			labels = ", ".join(Flag.Group(g).label for g in groups)
			self.message_user(
				request,
				f"Assigned {count} stems (from {queryset.count()} groups) to {user.username}. Review tasks ensured for {len(flags)} active flags in group(s): {labels}.",
				level=messages.SUCCESS,
			)
			return None

		users = get_user_model().objects.filter(is_active=True).order_by("username")
		request.current_app = self.admin_site.name
		preview_groups = list(queryset.order_by("source_line_no", "id"))
		# Default the checkbox selection to the union of stored groups.
		union: list[str] = []
		seen = set()
		for sg in preview_groups:
			for g in (getattr(sg, "flag_groups", None) or []):
				g = (g or "").strip()
				if not g or g in seen:
					continue
				seen.add(g)
				union.append(g)
		context = {
			**self.admin_site.each_context(request),
			"title": "Assign stem groups",
			"stem_groups": preview_groups,
			"users": users,
			"flag_groups": list(Flag.Group.choices),
			"current_flag_groups": union or [Flag.Group.PRIORITY],
			"action_name": "assign_selected_groups_to_user",
			"opts": self.model._meta,
		}
		return TemplateResponse(request, "admin/review_assign_stem_groups.html", context)

	def _assign_selected_groups_to_specific_user(self, request, queryset, user_id: int):
		allowed_groups = {c[0] for c in Flag.Group.choices}
		User = get_user_model()
		user = User.objects.filter(id=int(user_id), is_active=True).only("id", "username").first()
		if not user:
			self.message_user(request, "User not found.", level=messages.ERROR)
			return None

		# Default to the union of stored flag group(s) on the selected stem groups.
		union: list[str] = []
		seen = set()
		for sg in queryset:
			for g in (getattr(sg, "flag_groups", None) or []):
				g = (g or "").strip()
				if not g or g in seen:
					continue
				seen.add(g)
				union.append(g)
		groups = [g for g in union if g in allowed_groups]
		if not groups:
			self.message_user(
				request,
				"No flag group(s) set on these stem groups. Use 'Set flag group(s) for selected stem groups' first (or use the generic assign action).",
				level=messages.ERROR,
			)
			return None

		group_ids = list(queryset.values_list("id", flat=True))
		stem_ids = list(Stem.objects.filter(group_id__in=group_ids).values_list("id", flat=True))
		count = len(stem_ids)
		flags = list(Flag.objects.filter(is_active=True, group__in=groups).values_list("id", flat=True))
		if stem_ids and not flags:
			labels = ", ".join(Flag.Group(g).label for g in groups)
			self.message_user(
				request,
				f"No active flags found in selected group(s): {labels}.",
				level=messages.ERROR,
			)
			return None

		now = timezone.now()
		if stem_ids:
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

		labels = ", ".join(Flag.Group(g).label for g in groups)
		self.message_user(
			request,
			f"Assigned {count} stems (from {queryset.count()} groups) to {user.username}. Review tasks ensured for {len(flags)} active flags in group(s): {labels}.",
			level=messages.SUCCESS,
		)
		return None

	@admin.action(description="Set flag group(s) for selected stem groups")
	def set_flag_groups_for_selected_groups(self, request, queryset):
		if "apply" in request.POST:
			allowed_groups = {c[0] for c in Flag.Group.choices}
			groups = [g.strip() for g in request.POST.getlist("flag_groups") if (g or "").strip()]
			if not groups:
				self.message_user(request, "Select one or more flag groups.", level=messages.ERROR)
				return None
			invalid = [g for g in groups if g not in allowed_groups]
			if invalid:
				self.message_user(request, f"Invalid flag group(s): {', '.join(invalid)}.", level=messages.ERROR)
				return None

			uniq = []
			seen = set()
			for g in groups:
				if g in seen:
					continue
				seen.add(g)
				uniq.append(g)

			updated = 0
			for sg in queryset:
				sg.flag_groups = list(uniq)
				sg.save(update_fields=["flag_groups"])
				updated += 1

			labels = ", ".join(Flag.Group(g).label for g in uniq)
			self.message_user(request, f"Set flag group(s) for {updated} stem groups: {labels}.", level=messages.SUCCESS)
			return None

		request.current_app = self.admin_site.name
		preview_groups = list(queryset.order_by("source_line_no", "id"))
		context = {
			**self.admin_site.each_context(request),
			"title": "Set flag group(s) for stem groups",
			"stem_groups": preview_groups,
			"flag_groups": list(Flag.Group.choices),
			"current_flag_groups": [],
			"action_name": "set_flag_groups_for_selected_groups",
			"opts": self.model._meta,
		}
		return TemplateResponse(request, "admin/review_set_stem_group_flag_groups.html", context)

	@admin.action(description="Unassign selected stem groups")
	def unassign_selected_groups(self, request, queryset):
		group_ids = list(queryset.values_list("id", flat=True))
		if not group_ids:
			self.message_user(request, "No stem groups selected.", level=messages.WARNING)
			return

		# Unassign stems that belong to these groups.
		stems_qs = Stem.objects.filter(group_id__in=group_ids).exclude(assigned_to__isnull=True)
		stems_count = stems_qs.count()
		stems_qs.update(assigned_to=None, assigned_at=None)
		self.message_user(
			request,
			f"Unassigned {stems_count} stems across {len(group_ids)} stem groups.",
			level=messages.SUCCESS,
		)


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
