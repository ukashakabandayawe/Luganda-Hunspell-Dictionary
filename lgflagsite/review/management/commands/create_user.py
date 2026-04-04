from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
	help = "Create a Django user quickly (optionally staff/superuser)."

	def add_arguments(self, parser):
		parser.add_argument("--username", required=True)
		parser.add_argument("--password", required=True)
		parser.add_argument("--staff", action="store_true")
		parser.add_argument("--superuser", action="store_true")

	def handle(self, *args, **options):
		User = get_user_model()
		username = options["username"]
		password = options["password"]
		is_staff = bool(options["staff"] or options["superuser"])
		is_superuser = bool(options["superuser"])

		if User.objects.filter(username=username).exists():
			raise CommandError("User already exists")

		user = User.objects.create_user(username=username, password=password)
		user.is_staff = is_staff
		user.is_superuser = is_superuser
		user.save(update_fields=["is_staff", "is_superuser"])
		self.stdout.write(self.style.SUCCESS(f"Created user: {username} (staff={is_staff}, superuser={is_superuser})"))
