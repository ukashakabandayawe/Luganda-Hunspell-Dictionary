from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from review.models import Flag, Stem, StemFlagTask


class Command(BaseCommand):
	help = "Create StemFlagTask rows for stems and a list of flags."

	def add_arguments(self, parser):
		parser.add_argument("--flags", required=True, help="Comma-separated list of flag codes, e.g. PS,NP")
		parser.add_argument("--only-assigned", action="store_true", help="Only create tasks for stems that are assigned to a user")
		parser.add_argument("--limit", type=int, default=0, help="Optional limit on number of stems")

	@transaction.atomic
	def handle(self, *args, **options):
		flags_raw = (options["flags"] or "").strip()
		if not flags_raw:
			raise CommandError("--flags is required")
		flag_codes = [f.strip() for f in flags_raw.split(",") if f.strip()]
		if not flag_codes:
			raise CommandError("No valid flag codes")

		flags = list(Flag.objects.filter(code__in=flag_codes, is_active=True))
		found = {f.code for f in flags}
		missing = [c for c in flag_codes if c not in found]
		if missing:
			raise CommandError(f"Unknown/inactive flags: {', '.join(missing)}. Run sync_luganda_aff_flags first.")

		stems_qs = Stem.objects.all().order_by("source_line_no", "id")
		if options.get("only_assigned"):
			stems_qs = stems_qs.filter(assigned_to__isnull=False)
		limit = int(options.get("limit") or 0)
		if limit > 0:
			stems_qs = stems_qs[:limit]

		created = 0
		for stem in stems_qs:
			for flag in flags:
				obj, is_new = StemFlagTask.objects.get_or_create(stem=stem, flag=flag)
				if is_new:
					created += 1

		self.stdout.write(self.style.SUCCESS(f"Created {created} tasks"))
