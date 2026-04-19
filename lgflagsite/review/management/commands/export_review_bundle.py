from __future__ import annotations

import gzip
import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from review.offline_bundle import build_offline_review_bundle_payload


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

        payload = build_offline_review_bundle_payload(
            user=user,
            limit_examples=limit_examples,
            examples_for=examples_for,
        )

        # Compact JSON to keep bundles small.
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        with gzip.open(out_path, "wb", compresslevel=9) as f:
            f.write(raw)

        self.stdout.write(
            self.style.SUCCESS(
                "Bundle written: "
                f"{out_path} (stems={payload.get('summary', {}).get('stems')}, tasks={payload.get('summary', {}).get('tasks')}, examples={payload.get('summary', {}).get('examples')})"
            )
        )
