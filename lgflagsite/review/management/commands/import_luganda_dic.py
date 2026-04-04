from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from review.dic_io import parse_dic_entry_line
from review.hunspell import HunspellFlagMode, detect_flag_mode, merge_flags, split_long_flags
from review.models import Stem


class Command(BaseCommand):
	help = "Import stems from Luganda.dic into the database."

	def add_arguments(self, parser):
		parser.add_argument("--dic", type=str, default=str(getattr(settings, "HUNSPELL_DIC_SOURCE_PATH")))
		parser.add_argument("--aff", type=str, default=str(getattr(settings, "HUNSPELL_AFF_PATH")))
		parser.add_argument("--reset", action="store_true", help="Delete existing stems before import.")

	@transaction.atomic
	def handle(self, *args, **options):
		dic_path = Path(options["dic"]).resolve()
		aff_path = Path(options["aff"]).resolve()
		reset = bool(options["reset"])

		if not dic_path.exists():
			raise CommandError(f".dic not found: {dic_path}")
		if not aff_path.exists():
			raise CommandError(f".aff not found: {aff_path}")

		mode = detect_flag_mode(aff_path)
		self.stdout.write(self.style.NOTICE(f"Detected flag mode: {mode}"))

		if Stem.objects.exists() and not reset:
			raise CommandError("Stem table is not empty. Re-run with --reset if you want to replace it.")

		if reset:
			Stem.objects.all().delete()

		lines = dic_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=False)
		if not lines:
			raise CommandError(".dic is empty")

		created = 0
		updated = 0
		duplicate_lines = 0

		for idx, line in enumerate(lines):
			if idx == 0:
				continue  # count
			entry = parse_dic_entry_line(line)
			if not entry:
				continue

			stem_text = entry.stem
			stem, is_new = Stem.objects.get_or_create(
				text=stem_text,
				defaults={
					"flags_raw": entry.flags_raw or "",
					"trailing": entry.trailing or "",
					"source_line_no": idx,
				},
			)
			if is_new:
				created += 1
				continue

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

		self.stdout.write(self.style.SUCCESS(f"Imported stems: created={created}, updated={updated}, duplicate_lines={duplicate_lines}"))
