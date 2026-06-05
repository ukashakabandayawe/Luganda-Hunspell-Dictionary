from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from review.cli_progress import ProgressLine, raw_stream_for_command_stdout
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
        parser.add_argument(
            "--progress",
            choices=["auto", "on", "off"],
            default="auto",
            help="Show progress while building each bundle (auto=TTY only).",
        )

    def handle(self, *args, **options):
        raw_users = options.get("users") or []
        usernames = [str(u).strip() for u in raw_users if str(u).strip()]
        if not usernames:
            usernames = list(_DEFAULT_USERS)

        limit_opt = options.get("limit_examples")
        if limit_opt is None:
            limit_opt = options.get("limit-examples")
        if limit_opt is None:
            limit_opt = 120
        limit_examples = int(limit_opt)
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

        progress_mode = (options.get("progress") or "auto").strip().lower()
        if progress_mode not in {"auto", "on", "off"}:
            progress_mode = "auto"

        out_stream = raw_stream_for_command_stdout(self.stdout)
        progress = ProgressLine(
            out_stream,
            enabled=(progress_mode != "off"),
            force=(progress_mode == "on"),
        )

        for user_i, username in enumerate(usernames, start=1):
            user = by_username[username]
            out_path = (out_dir / f"bundle_{user.username}.json.gz").resolve()

            progress_cb = None
            if progress.enabled:
                progress.write(
                    progress.render(prefix=f"{user.username}", done=0, total=1, extra="tasks=0  examples=0"),
                    force=True,
                )
                progress_cb = progress.callback_counts(prefix=f"{user.username}")

            payload = build_offline_review_bundle_payload(
                user=user,
                limit_examples=limit_examples,
                examples_for=examples_for,
                progress_callback=progress_cb,
            )

            progress.finish()

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
