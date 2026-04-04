from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from review.models import Stem


class Command(BaseCommand):
	help = "Assign unassigned stems to a user (batch)."

	def add_arguments(self, parser):
		parser.add_argument("--user", required=True, help="Username to assign stems to")
		parser.add_argument("--limit", type=int, default=100, help="Number of stems to assign")

	@transaction.atomic
	def handle(self, *args, **options):
		username = options["user"]
		limit = int(options["limit"])
		if limit < 1:
			raise CommandError("--limit must be >= 1")

		User = get_user_model()
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist as ex:
			raise CommandError(str(ex))

		qs = Stem.objects.filter(assigned_to__isnull=True).order_by("source_line_no", "id")[:limit]
		count = qs.count()
		now = timezone.now()
		Stem.objects.filter(id__in=[s.id for s in qs]).update(assigned_to=user, assigned_at=now)
		self.stdout.write(self.style.SUCCESS(f"Assigned {count} stems to {username}"))
