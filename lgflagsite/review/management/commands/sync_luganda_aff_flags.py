from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from review.models import Flag


class Command(BaseCommand):
	help = "Sync Flag records from Luganda.aff (codes, types, descriptions)."

	def add_arguments(self, parser):
		parser.add_argument("--aff", type=str, default=str(getattr(settings, "HUNSPELL_AFF_PATH")))

	@transaction.atomic
	def handle(self, *args, **options):
		aff_path = Path(options["aff"]).resolve()
		if not aff_path.exists():
			raise CommandError(f".aff not found: {aff_path}")

		# Canonical `# XX = ...` definitions live near the top; don't scan the whole file.
		canonical: dict[str, str] = {}
		try:
			with aff_path.open("r", encoding="utf-8", errors="replace") as f_top:
				for _ in range(5000):
					raw = f_top.readline()
					if not raw:
						break
					line = raw.strip()
					if not line.startswith("#"):
						continue
					m = re.match(r"^#\s*([^\s=]{1,16})\s*=\s*(.+?)\s*$", line)
					if not m:
						continue
					code = m.group(1).strip()
					desc = m.group(2).strip()
					if code and code not in canonical:
						canonical[code] = desc
		except OSError as ex:
			raise CommandError(str(ex))

		# code -> (affix_type 'P'|'S', description, group, aff_order)
		flags: dict[str, tuple[str, str, str, int]] = {}
		advanced_on = False

		def clean_comment(s: str) -> str:
			s = s.strip().lstrip("#").strip()
			for marker in (" e.g.", " E.g.", " for example:", " For example:"):
				if marker in s:
					s = s.split(marker, 1)[0].rstrip(" :")
			return s

		comment_block: list[str] = []
		try:
			with aff_path.open("r", encoding="utf-8", errors="replace") as f:
				for line_no, raw in enumerate(f, start=1):
					if line_no % 200000 == 0:
						self.stdout.write(f"...scanned {line_no:,} lines")
					line = (raw or "").rstrip("\n")
					t = line.strip()
					if not t:
						comment_block = []
						continue
					if t.startswith("#"):
						c = clean_comment(t)
						if c and not c.lower().startswith(("e.g.", "for example:", "since ")):
							comment_block.append(c)
						continue

					parts = t.split()
					if len(parts) >= 4 and parts[0] in {"PFX", "SFX"} and parts[2] in {"Y", "N"}:
						code = parts[1]
						affix_type = "P" if parts[0] == "PFX" else "S"
						if code == "GA":
							advanced_on = True
						group = Flag.Group.ADVANCED if advanced_on else Flag.Group.PRIORITY
						if code not in flags:
							aff_order = len(flags) + 1
							desc = canonical.get(code) or (" ".join(comment_block[:2]).strip() if comment_block else "")
							flags[code] = (affix_type, desc, group, aff_order)
						if code == "JP":
							advanced_on = False
						comment_block = []
						continue

					comment_block = []
		except OSError as ex:
			raise CommandError(str(ex))

		seen = set(flags.keys())
		created = 0
		updated = 0

		for code, (t, desc, group, aff_order) in flags.items():
			obj, is_new = Flag.objects.get_or_create(
				code=code,
				defaults={
					"affix_type": t,
					"description": desc,
					"is_active": True,
					"group": group or Flag.Group.PRIORITY,
					"aff_order": int(aff_order),
				},
			)
			if is_new:
				created += 1
				continue
			changed = False
			if t and obj.affix_type != t:
				obj.affix_type = t
				changed = True
			if desc and obj.description != desc:
				obj.description = desc
				changed = True
			if not obj.is_active:
				obj.is_active = True
				changed = True
			if obj.aff_order != int(aff_order):
				obj.aff_order = int(aff_order)
				changed = True
			# Auto-mark GA..JP as Advanced based on .aff order; do not override other manual groupings.
			if group == Flag.Group.ADVANCED and obj.group != Flag.Group.ADVANCED:
				obj.group = Flag.Group.ADVANCED
				changed = True
			if changed:
				obj.save()
				updated += 1

		Flag.objects.exclude(code__in=seen).update(is_active=False)
		self.stdout.write(self.style.SUCCESS(f"Synced flags: created={created}, updated={updated}, active={len(seen)}"))
