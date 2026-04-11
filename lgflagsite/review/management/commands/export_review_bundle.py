from __future__ import annotations

import gzip
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from review.hunspell import generate_examples_for_flag, get_flag_description
from review.models import Stem, StemFlagTask


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Command(BaseCommand):
    help = "Export an offline review bundle (stems + tasks + precomputed examples) for one user."

    def add_arguments(self, parser):
        parser.add_argument("--user", required=True, help="Username to export a bundle for")
        parser.add_argument(
            "--out",
            default="",
            help="Output path. Defaults to DATA_DIR/bundles/bundle_<username>.json.gz",
        )
        parser.add_argument(
            "--limit-examples",
            type=int,
            default=120,
            help="Max examples per task (default: 120)",
        )
        parser.add_argument(
            "--examples-for",
            choices=["pending", "all"],
            default="pending",
            help="Generate examples only for pending tasks (default) or all tasks.",
        )

    def handle(self, *args, **options):
        username = (options.get("user") or "").strip()
        if not username:
            raise CommandError("--user is required")

        limit_examples = int(options.get("limit_examples") or options.get("limit-examples") or 120)
        if limit_examples < 0:
            raise CommandError("--limit-examples must be >= 0")

        examples_for = (options.get("examples_for") or options.get("examples-for") or "pending").strip().lower()
        if examples_for not in {"pending", "all"}:
            raise CommandError("--examples-for must be 'pending' or 'all'")

        User = get_user_model()
        user = User.objects.filter(username=username).only("id", "username").first()
        if not user:
            raise CommandError(f"User not found: {username}")

        repo_dir = Path(getattr(settings, "REPO_DIR"))
        data_dir = Path(getattr(settings, "DATA_DIR"))
        aff_path = Path(getattr(settings, "HUNSPELL_AFF_PATH")).resolve()

        if not aff_path.exists():
            raise CommandError(f"Hunspell .aff not found: {aff_path}")

        out_raw = (options.get("out") or "").strip()
        if out_raw:
            out_path = Path(out_raw).expanduser().resolve()
        else:
            out_path = (data_dir / "bundles" / f"bundle_{user.username}.json.gz").resolve()

        out_path.parent.mkdir(parents=True, exist_ok=True)

        stems = list(
            Stem.objects.filter(assigned_to=user)
            .only("id", "text", "source_line_no")
            .order_by("source_line_no", "id")
        )

        stem_ids = [s.id for s in stems]
        tasks = (
            StemFlagTask.objects.filter(stem_id__in=stem_ids)
            .select_related("flag", "stem")
            .order_by("stem__source_line_no", "stem_id", "flag__code")
        )

        tasks_by_stem: dict[int, list[StemFlagTask]] = {}
        for t in tasks:
            tasks_by_stem.setdefault(t.stem_id, []).append(t)

        total_tasks = 0
        total_examples = 0

        stem_rows = []
        for s in stems:
            task_rows = []
            for t in tasks_by_stem.get(s.id, []):
                total_tasks += 1
                code = t.flag.code
                desc = t.flag.description or get_flag_description(aff_path, code) or ""

                include_examples = examples_for == "all" or t.status == StemFlagTask.Status.PENDING
                examples: list[str] = []
                if include_examples and limit_examples > 0:
                    examples = generate_examples_for_flag(aff_path, code, s.text, limit=limit_examples)
                    total_examples += len(examples)

                task_rows.append(
                    {
                        "task_id": int(t.id),
                        "flag": code,
                        "status": t.status,
                        "description": desc,
                        "examples": examples,
                    }
                )

            stem_rows.append(
                {
                    "stem": s.text,
                    "source_line_no": int(s.source_line_no or 0),
                    "tasks": task_rows,
                }
            )

        payload = {
            "schema": 1,
            "generated_at": _utc_now_iso(),
            "repo_dir": str(repo_dir),
            "user": {"id": int(user.id), "username": user.username},
            "aff": {
                "path": str(aff_path),
                "mtime_ns": aff_path.stat().st_mtime_ns,
                "size": aff_path.stat().st_size,
            },
            "example_limit": limit_examples,
            "examples_for": examples_for,
            "stems": stem_rows,
            "summary": {
                "stems": len(stems),
                "tasks": total_tasks,
                "examples": total_examples,
            },
        }

        # Compact JSON to keep bundles small.
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        with gzip.open(out_path, "wb", compresslevel=9) as f:
            f.write(raw)

        self.stdout.write(
            self.style.SUCCESS(
                f"Bundle written: {out_path} (stems={len(stems)}, tasks={total_tasks}, examples={total_examples})"
            )
        )
