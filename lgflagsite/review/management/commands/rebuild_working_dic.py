from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from review.dic_io import rebuild_working_dic
from review.hunspell import detect_flag_mode
from review.models import StemFlagTask
from review.services import build_approved_flags_map, working_dic_path_for_user_id


class Command(BaseCommand):
	help = "Rebuild the server-side working Luganda.dic (copy source, then apply all approved tasks)."

	def add_arguments(self, parser):
		parser.add_argument(
			"--user-id",
			dest="user_id",
			type=int,
			default=0,
			help="If set, rebuild that user's personal working .dic under WORKING_DIR/users/<id>/Luganda.dic",
		)
		parser.add_argument("--aff", type=str, default=str(getattr(settings, "HUNSPELL_AFF_PATH")))
		parser.add_argument("--source-dic", dest="source_dic", type=str, default=str(getattr(settings, "HUNSPELL_DIC_SOURCE_PATH")))
		parser.add_argument("--working-dic", dest="working_dic", type=str, default=str(getattr(settings, "WORKING_DIC_PATH")))

	def handle(self, *args, **options):
		user_id = int(options.get("user_id") or 0)
		aff_path = Path(options["aff"]).resolve()
		source_dic = Path(options["source_dic"]).resolve()
		working_dic = working_dic_path_for_user_id(user_id).resolve() if user_id > 0 else Path(options["working_dic"]).resolve()

		if not aff_path.exists():
			raise CommandError(f".aff not found: {aff_path}")
		if not source_dic.exists():
			raise CommandError(f"Source .dic not found: {source_dic}")

		mode = detect_flag_mode(aff_path)
		qs = StemFlagTask.objects.all()
		if user_id > 0:
			qs = qs.filter(decided_by_id=user_id)
		approved_map = build_approved_flags_map(qs)

		total_matched, total_changed, _, _ = rebuild_working_dic(source_dic, working_dic, approved_map, mode)
		label = "Working .dic" if user_id <= 0 else f"User {user_id} working .dic"
		self.stdout.write(self.style.SUCCESS(f"{label} rebuilt: matched={total_matched}, changed={total_changed} -> {working_dic}"))
