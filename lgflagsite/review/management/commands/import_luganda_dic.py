from __future__ import annotations

from pathlib import Path
import re
from collections import Counter
from typing import Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count, Max, Min, Q
from django.utils import timezone

from review.dic_io import parse_dic_entry_line
from review.hunspell import HunspellFlagMode, detect_flag_mode, merge_flags, split_long_flags
from review.models import Stem, StemGroup


_GROUP_RE = re.compile(r"^#\s*-+\s*(.*?)\s*-+\s*#\s*$")


def _parse_group_marker(line: str) -> Optional[tuple[str, str]]:
	"""Return ('start', title) or ('end','') when the line is a group marker.

	We treat comment lines like:
	  # --- faako --- #
	  # -------- okweyanza(to thank) -------- #
	as a group start.

	And comment lines that are only dashes as a group end:
	  # ------------------ #
	"""

	t = (line or "").strip()
	if not t.startswith("#"):
		return None
	if t == "#":
		return None

	# Strip leading and trailing comment markers.
	content = t.lstrip("#").strip()
	if content.endswith("#"):
		content = content[:-1].strip()
	if not content:
		return None

	# End marker: only dashes (and optional spaces).
	if content and all(ch in {"-", " "} for ch in content):
		return ("end", "")

	m = _GROUP_RE.match(t)
	if not m:
		return None

	middle = (m.group(1) or "").strip()
	if not middle:
		return None
	# Start marker should contain something meaningful (avoid false-positives).
	if not any(ch.isalnum() for ch in middle):
		return None
	return ("start", middle)


class Command(BaseCommand):
	help = "Import stems from Luganda.dic into the database."

	def add_arguments(self, parser):
		parser.add_argument("--dic", type=str, default=str(getattr(settings, "HUNSPELL_DIC_SOURCE_PATH")))
		parser.add_argument("--aff", type=str, default=str(getattr(settings, "HUNSPELL_AFF_PATH")))
		parser.add_argument("--reset", action="store_true", help="Delete existing stems before import.")
		parser.add_argument(
			"--upsert",
			action="store_true",
			help="Create missing stems and update group links/flags for existing stems without deleting review progress.",
		)
		parser.add_argument(
			"--update-groups-only",
			action="store_true",
			help="Only parse comment group blocks and attach Stem.group for existing stems. Does not create/delete stems.",
		)

	@transaction.atomic
	def handle(self, *args, **options):
		dic_path = Path(options["dic"]).resolve()
		aff_path = Path(options["aff"]).resolve()
		reset = bool(options["reset"])
		upsert = bool(options.get("upsert"))
		update_groups_only = bool(options.get("update_groups_only"))

		if update_groups_only and reset:
			raise CommandError("--update-groups-only cannot be combined with --reset")
		if upsert and reset:
			raise CommandError("--upsert cannot be combined with --reset")
		if upsert and update_groups_only:
			raise CommandError("--upsert cannot be combined with --update-groups-only")

		if not dic_path.exists():
			raise CommandError(f".dic not found: {dic_path}")
		if not aff_path.exists():
			raise CommandError(f".aff not found: {aff_path}")

		mode = detect_flag_mode(aff_path)
		self.stdout.write(self.style.NOTICE(f"Detected flag mode: {mode}"))

		if Stem.objects.exists() and not reset and not update_groups_only and not upsert:
			raise CommandError(
				"Stem table is not empty. Use --reset to replace it, --upsert to add missing stems safely, or --update-groups-only to only attach groups."
			)

		if reset:
			Stem.objects.all().delete()
			StemGroup.objects.all().delete()

		lines = dic_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=False)
		if not lines:
			raise CommandError(".dic is empty")

		created = 0
		updated = 0
		duplicate_lines = 0
		missing_stems_created = 0
		groups_seen = 0
		current_group: StemGroup | None = None
		first_seen_line_no: dict[str, int] = {}
		group_first_seen_line_no: dict[str, int] = {}
		group_assignee_cache: dict[int, int | None] = {}

		def _peek_group_sample_stems(start_idx: int, *, max_stems: int = 8, max_lines: int = 800) -> list[str]:
			"""Peek ahead to sample stems inside the current group block.

			Used as a heuristic to map a moved+renamed group title back to the existing
			DB StemGroup by looking at which group the stems previously belonged to.
			"""
			out: list[str] = []
			limit = min(len(lines), int(start_idx) + int(max_lines))
			for j in range(int(start_idx) + 1, limit):
				m = _parse_group_marker(lines[j])
				if m is not None and m[0] == "end":
					break
				entry = parse_dic_entry_line(lines[j])
				if not entry:
					continue
				out.append(entry.stem)
				if len(out) >= int(max_stems):
					break
			return out

		def _single_assignee_id_for_group(group_id: int) -> int | None:
			"""Return a user_id if all *assigned* stems in the group share one user.

			If the group has no assigned stems, or multiple assignees, return None.
			We intentionally allow unassigned stems: the goal is to keep group-level
			assignment stable when new stems are imported.
			"""
			cached = group_assignee_cache.get(int(group_id), "__missing__")
			if cached != "__missing__":
				return cached

			agg = Stem.objects.filter(group_id=int(group_id)).aggregate(
				assigned_users=Count(
					"assigned_to_id",
					filter=Q(assigned_to__isnull=False),
					distinct=True,
				),
				min_user=Min("assigned_to_id", filter=Q(assigned_to__isnull=False)),
				max_user=Max("assigned_to_id", filter=Q(assigned_to__isnull=False)),
			)
			assigned_users = int(agg.get("assigned_users") or 0)
			min_user = agg.get("min_user")
			max_user = agg.get("max_user")
			if assigned_users == 1 and min_user is not None and min_user == max_user:
				group_assignee_cache[int(group_id)] = int(min_user)
				return int(min_user)

			group_assignee_cache[int(group_id)] = None
			return None

		for idx, line in enumerate(lines):
			if idx == 0:
				continue  # count

			marker = _parse_group_marker(line)
			if marker is not None:
				kind, title = marker
				if kind == "end":
					current_group = None
				else:
					groups_seen += 1
					# Stable identity rules:
					# 1) Prefer matching by title (robust if lines shift when you insert words).
					# 2) If the title doesn't exist yet, fall back to matching by source_line_no
					#    to detect in-place renames.
					# 3) If neither match, create a new group.
					created = False
					first_line_in_file = group_first_seen_line_no.setdefault(title, int(idx))

					current_group = StemGroup.objects.filter(title=title).only("id", "title", "source_line_no").first()
					if current_group is not None:
						# Keep ordering aligned to current file (use earliest occurrence within this file).
						if int(getattr(current_group, "source_line_no", 0) or 0) != int(first_line_in_file):
							current_group.source_line_no = int(first_line_in_file)
							current_group.save(update_fields=["source_line_no"])
					else:
						existing_at_line = (
							StemGroup.objects.filter(source_line_no=int(idx))
							.only("id", "title", "source_line_no")
							.order_by("id")
						)
						current_group = existing_at_line.first()
						if current_group is not None:
							# Rename in-place (line-based fallback). This keeps existing stems/tasks/assignments.
							conflict = (
								StemGroup.objects.filter(title=title)
								.exclude(id=current_group.id)
								.exists()
							)
							if conflict:
								raise CommandError(
									(
										"Cannot rename StemGroup at line "
										f"{idx} from '{current_group.title}' to '{title}' "
										"because that title already exists. "
										"Choose a unique group title in Luganda.dic."
									)
								)
							fields = []
							if (current_group.title or "") != title:
								current_group.title = title
								fields.append("title")
							if int(getattr(current_group, "source_line_no", 0) or 0) != int(first_line_in_file):
								current_group.source_line_no = int(first_line_in_file)
								fields.append("source_line_no")
							if fields:
								current_group.save(update_fields=fields)
						else:
							# Heuristic: moved+renamed group.
							# If this title is new and the header line doesn't match an existing group,
							# try to identify the prior group by the stems inside this block.
							sample = _peek_group_sample_stems(idx)
							if sample:
								group_ids = list(
									Stem.objects.filter(text__in=sample)
									.exclude(group_id__isnull=True)
									.values_list("group_id", flat=True)
								)
								if group_ids:
									counts = Counter(int(gid) for gid in group_ids if gid)
									cand_id, cand_hits = counts.most_common(1)[0]
									found = len(group_ids)
									# Require a strong majority to avoid accidental remaps.
									if found >= 3 and cand_hits >= 3 and (cand_hits / max(1, found)) >= 0.75:
										candidate = (
											StemGroup.objects.filter(id=int(cand_id))
											.only("id", "title", "source_line_no")
											.first()
										)
										if candidate is not None:
											conflict = StemGroup.objects.filter(title=title).exclude(id=candidate.id).exists()
											if conflict:
												raise CommandError(
													(
														"Cannot rename stem group (heuristic match) to "
														f"'{title}' because that title already exists."
													)
											)
											fields = []
											if (candidate.title or "") != title:
												candidate.title = title
												fields.append("title")
											if int(getattr(candidate, "source_line_no", 0) or 0) != int(first_line_in_file):
												candidate.source_line_no = int(first_line_in_file)
												fields.append("source_line_no")
											if fields:
												candidate.save(update_fields=fields)
											current_group = candidate

							if current_group is None:
								current_group = StemGroup.objects.create(title=title, source_line_no=int(first_line_in_file))
								created = True
				continue

			entry = parse_dic_entry_line(line)
			if not entry:
				continue

			# Preserve source ordering: always use the first occurrence in the file.
			stem_first_line = first_seen_line_no.setdefault(entry.stem, idx)

			if update_groups_only:
				stem = Stem.objects.filter(text=entry.stem).only("id", "group_id").first()
				if stem is None:
					continue
				# If this stem used to be in a group due to a missing end marker,
				# and its first occurrence is now outside any group, clear it.
				if current_group is None and int(stem_first_line) == int(idx):
					if stem.group_id is not None:
						Stem.objects.filter(id=stem.id).update(group=None)
						updated += 1
					continue
				if current_group is not None and stem.group_id != current_group.id:
					Stem.objects.filter(id=stem.id).update(group=current_group)
					updated += 1
				continue

			if upsert:
				defaults = {
					"group": current_group,
					"flags_raw": entry.flags_raw or "",
					"trailing": entry.trailing or "",
					"source_line_no": stem_first_line,
				}
				if current_group is not None:
					assignee_id = _single_assignee_id_for_group(int(current_group.id))
					if assignee_id is not None:
						defaults["assigned_to_id"] = int(assignee_id)
						defaults["assigned_at"] = timezone.now()

				stem, is_new = Stem.objects.get_or_create(
					text=entry.stem,
					defaults=defaults,
				)
				if is_new:
					missing_stems_created += 1
				else:
					fields_to_update = []
					# Attach/refresh group.
					if current_group is not None and stem.group_id != current_group.id:
						stem.group = current_group
						fields_to_update.append("group")
					# If this stem's first occurrence is now outside any group,
					# clear its group. This fixes cases where a missing group end marker
					# previously caused later stems to be incorrectly grouped.
					if current_group is None and int(stem_first_line) == int(idx) and stem.group_id is not None:
						stem.group = None
						fields_to_update.append("group")
					# If the group already has a single assignee, keep assignments stable by
					# assigning any previously-unassigned stems we encounter during sync.
					if current_group is not None and getattr(stem, "assigned_to_id", None) is None:
						assignee_id = _single_assignee_id_for_group(int(current_group.id))
						if assignee_id is not None:
							stem.assigned_to_id = int(assignee_id)
							stem.assigned_at = timezone.now()
							fields_to_update.extend(["assigned_to", "assigned_at"])
					# Keep ordering in sync with current file.
					if int(stem.source_line_no or 0) != int(stem_first_line):
						stem.source_line_no = stem_first_line
						fields_to_update.append("source_line_no")
					# Best-effort merge flags.
					if entry.flags_raw and entry.flags_raw != (stem.flags_raw or ""):
						if mode == HunspellFlagMode.LONG:
							to_add = set(split_long_flags(entry.flags_raw))
						else:
							to_add = {entry.flags_raw}
						merged = merge_flags(stem.flags_raw or "", to_add, mode)
						if merged != (stem.flags_raw or ""):
							stem.flags_raw = merged
							fields_to_update.append("flags_raw")
					if fields_to_update:
						stem.save(update_fields=fields_to_update)
						updated += 1
				continue

			stem_text = entry.stem
			stem, is_new = Stem.objects.get_or_create(
				text=stem_text,
				defaults={
					"group": current_group,
					"flags_raw": entry.flags_raw or "",
					"trailing": entry.trailing or "",
					"source_line_no": stem_first_line,
				},
			)
			if is_new:
				created += 1
				continue

			if current_group is not None and stem.group_id is None:
				stem.group = current_group
				stem.save(update_fields=["group"])

			# Duplicate stem in file: best-effort merge flags and keep the first trailing.
			duplicate_lines += 1
			if entry.flags_raw and entry.flags_raw != (stem.flags_raw or ""):
				if mode == HunspellFlagMode.LONG:
					to_add = set(split_long_flags(entry.flags_raw))
				else:
					to_add = {entry.flags_raw}
				merged = merge_flags(stem.flags_raw or "", to_add, mode)
				if merged != (stem.flags_raw or ""):
					stem.flags_raw = merged
					stem.save(update_fields=["flags_raw"])
					updated += 1

		if update_groups_only:
			self.stdout.write(self.style.SUCCESS(f"Updated stem groups: updated={updated}, groups_seen={groups_seen}"))
		elif upsert:
			self.stdout.write(
				self.style.SUCCESS(
					f"Upserted stems: missing_stems_created={missing_stems_created}, updated={updated}, groups_seen={groups_seen}"
				)
			)
		else:
			self.stdout.write(
				self.style.SUCCESS(
					f"Imported stems: created={created}, updated={updated}, duplicate_lines={duplicate_lines}, groups_seen={groups_seen}"
				)
			)
