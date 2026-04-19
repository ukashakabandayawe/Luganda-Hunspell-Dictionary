from __future__ import annotations

from pathlib import Path
import re
from typing import Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

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
					current_group, _ = StemGroup.objects.get_or_create(
						source_line_no=idx,
						defaults={"title": title},
					)
					# If title changed in file, keep DB in sync.
					if current_group.title != title:
						current_group.title = title
						current_group.save(update_fields=["title"])
				continue

			entry = parse_dic_entry_line(line)
			if not entry:
				continue

			# Preserve source ordering: always use the first occurrence in the file.
			stem_first_line = first_seen_line_no.setdefault(entry.stem, idx)

			if update_groups_only:
				if current_group is None:
					continue
				stem = Stem.objects.filter(text=entry.stem).only("id", "group_id").first()
				if stem is None:
					continue
				if stem.group_id != current_group.id:
					Stem.objects.filter(id=stem.id).update(group=current_group)
					updated += 1
				continue

			if upsert:
				stem, is_new = Stem.objects.get_or_create(
					text=entry.stem,
					defaults={
						"group": current_group,
						"flags_raw": entry.flags_raw or "",
						"trailing": entry.trailing or "",
						"source_line_no": stem_first_line,
					},
				)
				if is_new:
					missing_stems_created += 1
				else:
					fields_to_update = []
					# Attach/refresh group.
					if current_group is not None and stem.group_id != current_group.id:
						stem.group = current_group
						fields_to_update.append("group")
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
