from __future__ import annotations

import gzip
import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from review.offline_bundle import build_offline_review_bundle_payload


_DEFAULT_USERS = [
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
]


class Command(BaseCommand):
    help = "Export offline review bundles (.json.gz) for multiple users in one run."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            nargs="+",
            default=[],
            help="Usernames to export (space-separated). Defaults to alfa..lima.",
        )
        parser.add_argument(
            "--out-dir",
            default="",
            help="Output directory. Defaults to DATA_DIR/bundles/.",
        )
        parser.add_argument(
            "--limit-examples",
            type=int,
            default=120,
            help="Max examples per task (default: 120). Use 0 for fastest export.",
        )
        parser.add_argument(
            "--examples-for",
            choices=["pending", "all"],
            default="pending",
            help="Generate examples only for pending tasks (default) or all tasks.",
        )

    def handle(self, *args, **options):
        raw_users = options.get("users") or []
        usernames = [str(u).strip() for u in raw_users if str(u).strip()]
        if not usernames:
            usernames = list(_DEFAULT_USERS)

        limit_examples = int(options.get("limit_examples") or options.get("limit-examples") or 120)
        if limit_examples < 0:
            raise CommandError("--limit-examples must be >= 0")

        examples_for = (options.get("examples_for") or options.get("examples-for") or "pending").strip().lower()
        if examples_for not in {"pending", "all"}:
            raise CommandError("--examples-for must be 'pending' or 'all'")

        data_dir = Path(getattr(settings, "DATA_DIR"))
        out_dir_raw = (options.get("out_dir") or options.get("out-dir") or "").strip()
        out_dir = Path(out_dir_raw).expanduser().resolve() if out_dir_raw else (data_dir / "bundles").resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        User = get_user_model()
        users = list(User.objects.filter(username__in=usernames).only("id", "username"))
        by_username = {u.username: u for u in users}
        missing = [u for u in usernames if u not in by_username]
        if missing:
            raise CommandError(f"User(s) not found: {', '.join(missing)}")

        total_stems = 0
        total_tasks = 0
        total_examples = 0

        for username in usernames:
            user = by_username[username]
            out_path = (out_dir / f"bundle_{user.username}.json.gz").resolve()

            payload = build_offline_review_bundle_payload(
                user=user,
                limit_examples=limit_examples,
                examples_for=examples_for,
            )

            raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            with gzip.open(out_path, "wb", compresslevel=9) as f:
                f.write(raw)

            summary = payload.get("summary", {}) or {}
            stems_n = int(summary.get("stems") or 0)
            tasks_n = int(summary.get("tasks") or 0)
            ex_n = int(summary.get("examples") or 0)

            total_stems += stems_n
            total_tasks += tasks_n
            total_examples += ex_n

            self.stdout.write(
                self.style.SUCCESS(
                    f"Bundle written: {out_path} (stems={stems_n}, tasks={tasks_n}, examples={ex_n})"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Batch complete: "
                f"users={len(usernames)}, stems={total_stems}, tasks={total_tasks}, examples={total_examples} -> {out_dir}"
            )
        )
