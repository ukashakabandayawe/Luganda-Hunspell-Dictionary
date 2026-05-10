from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


NATO_USERNAMES = [
	"alfa",
	"bravo",
	"charlie",
	"delta",
	"echo",
	"foxtrot",
	"golf",
	"hotel",
	"india",
	"juliett",
	"kilo",
	"lima",
	"mike",
	"november",
	"oscar",
	"papa",
	"quebec",
	"romeo",
	"sierra",
	"tango",
	"uniform",
	"victor",
	"whiskey",
	"xray",
	"yankee",
	"zulu",
]


class Command(BaseCommand):
	help = (
		"Create reviewer user accounts named after the NATO phonetic alphabet. "
		"By default, users are created with an unusable password (username-only identity)."
	)

	def add_arguments(self, parser):
		parser.add_argument(
			"--count",
			type=int,
			default=21,
			help="How many reviewers to create (max 26). Default: 21.",
		)
		parser.add_argument(
			"--password",
			type=str,
			default="",
			help="Optional: set the same password for all created users.",
		)

	def handle(self, *args, **options):
		User = get_user_model()
		count = int(options.get("count") or 0)
		password = (options.get("password") or "").strip()

		if count < 1:
			self.stdout.write(self.style.WARNING("Nothing to do (--count < 1)."))
			return
		if count > len(NATO_USERNAMES):
			count = len(NATO_USERNAMES)

		created = 0
		skipped = 0
		updated = 0

		for username in NATO_USERNAMES[:count]:
			obj = User.objects.filter(username=username).first()
			if obj is not None:
				skipped += 1
				# Ensure reviewers aren't accidentally staff/superusers.
				changed = False
				if getattr(obj, "is_staff", False):
					obj.is_staff = False
					changed = True
				if getattr(obj, "is_superuser", False):
					obj.is_superuser = False
					changed = True
				if getattr(obj, "is_active", True) is False:
					obj.is_active = True
					changed = True
				if password:
					obj.set_password(password)
					changed = True
				if changed:
					obj.save()
					updated += 1
				continue

			user = User.objects.create_user(username=username)
			user.is_staff = False
			user.is_superuser = False
			user.is_active = True
			if password:
				user.set_password(password)
			else:
				user.set_unusable_password()
			user.save()
			created += 1

		self.stdout.write(
			self.style.SUCCESS(
				f"NATO reviewers: created={created}, updated={updated}, already_existed={skipped} (count={count})"
			)
		)
