from __future__ import annotations

import gzip
import json
from datetime import datetime, timezone
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone as dj_timezone

from review.models import Flag, ReviewDecision, Stem, StemFlagTask


def _parse_iso_datetime(value: str | None):
    if not value:
        return None
    s = value.strip()
    if not s:
        return None

    # Support a trailing 'Z' (UTC) which datetime.fromisoformat doesn't accept.
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _read_json_or_gz(path: Path):
    if path.suffix.lower() == ".gz":
        with gzip.open(path, "rb") as f:
            return json.loads(f.read().decode("utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


class Command(BaseCommand):
    help = "Import offline review decisions (JSON) into the database for a user."

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True, help="Path to decisions JSON (.json or .json.gz)")
        parser.add_argument("--user", required=True, help="Username the decisions belong to")
        parser.add_argument("--dry-run", action="store_true", help="Validate and report, but do not write changes")

    def handle(self, *args, **options):
        file_raw = (options.get("file") or "").strip()
        username = (options.get("user") or "").strip()
        dry_run = bool(options.get("dry_run") or options.get("dry-run"))

        if not file_raw:
            raise CommandError("--file is required")
        if not username:
            raise CommandError("--user is required")

        path = Path(file_raw).expanduser().resolve()
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        User = get_user_model()
        user = User.objects.filter(username=username).only("id", "username").first()
        if not user:
            raise CommandError(f"User not found: {username}")

        payload = _read_json_or_gz(path)
        schema = int(payload.get("schema") or 0)
        if schema != 1:
            raise CommandError(f"Unsupported decisions schema: {schema} (expected 1)")

        decisions = payload.get("decisions")
        if not isinstance(decisions, list):
            raise CommandError("Invalid file: 'decisions' must be a list")

        applied = 0
        skipped_same = 0
        missing_stem = 0
        missing_flag = 0
        missing_task = 0
        invalid = 0

        for row in decisions:
            if not isinstance(row, dict):
                invalid += 1
                continue

            stem_text = (row.get("stem") or "").strip()
            flag_code = (row.get("flag") or "").strip()
            decision_raw = (row.get("decision") or "").strip().lower()
            note = (row.get("note") or "").strip()
            decided_at = _parse_iso_datetime(row.get("decided_at"))

            if not stem_text or not flag_code:
                invalid += 1
                continue

            if decision_raw in {"approved", "approve"}:
                new_status = StemFlagTask.Status.APPROVED
            elif decision_raw in {"rejected", "reject"}:
                new_status = StemFlagTask.Status.REJECTED
            else:
                invalid += 1
                continue

            stem = Stem.objects.filter(text=stem_text).only("id", "text").first()
            if not stem:
                missing_stem += 1
                continue

            flag = Flag.objects.filter(code=flag_code).only("id", "code").first()
            if not flag:
                missing_flag += 1
                continue

            task = (
                StemFlagTask.objects.filter(stem_id=stem.id, flag_id=flag.id)
                .select_related("stem", "flag")
                .first()
            )
            if not task:
                missing_task += 1
                continue

            # Basic idempotency: if task already matches and the last logged decision matches too, skip.
            if task.status == new_status and task.decided_by_id == user.id:
                last = (
                    ReviewDecision.objects.filter(task_id=task.id, user_id=user.id)
                    .order_by("-created_at")
                    .only("decision", "note")
                    .first()
                )
                if last and (last.decision == new_status and (last.note or "") == (note or "")):
                    skipped_same += 1
                    continue

            if dry_run:
                applied += 1
                continue

            # If decided_at not provided, still set decided_at to now.
            task.set_status(new_status, user, note=note, decided_at=decided_at or dj_timezone.now())
            applied += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Import summary: "
                f"applied={applied}, skipped_same={skipped_same}, "
                f"missing_stem={missing_stem}, missing_flag={missing_flag}, missing_task={missing_task}, invalid={invalid}"
            )
        )
