from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from review.cli_progress import ProgressLine, raw_stream_for_command_stdout
from review.offline_bundle import build_offline_review_bundle_payload


class Command(BaseCommand):
    help = "Export an offline review bundle (stems + tasks + precomputed examples) for one user."

    def add_arguments(self, parser):
        parser.add_argument("--user", required=True, help="Username to export a bundle for")
        parser.add_argument(
            "--format",
            choices=["gz", "zip"],
            default="zip",
            help="Output format: 'zip' (bundle + Luganda.dic) or 'gz' (bundle only). Default: zip.",
        )
        parser.add_argument(
            "--out",
            default="",
            help="Output path. Defaults to DATA_DIR/bundles/bundle_<username>.<ext>",
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
        parser.add_argument(
            "--progress",
            choices=["auto", "on", "off"],
            default="auto",
            help="Show progress while building the bundle (auto=TTY only).",
        )

    def handle(self, *args, **options):
        username = (options.get("user") or "").strip()
        if not username:
            raise CommandError("--user is required")

        fmt = (options.get("format") or "zip").strip().lower()
        if fmt not in {"gz", "zip"}:
            raise CommandError("--format must be 'gz' or 'zip'")

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

        User = get_user_model()
        user = User.objects.filter(username=username).only("id", "username").first()
        if not user:
            raise CommandError(f"User not found: {username}")

        repo_dir = Path(getattr(settings, "REPO_DIR"))
        data_dir = Path(getattr(settings, "DATA_DIR"))
        aff_path = Path(getattr(settings, "HUNSPELL_AFF_PATH")).resolve()

        if not aff_path.exists():
            raise CommandError(f"Hunspell .aff not found: {aff_path}")

        dic_path = Path(getattr(settings, "HUNSPELL_DIC_SOURCE_PATH")).resolve()
        if not dic_path.exists():
            raise CommandError(f"Hunspell .dic not found: {dic_path}")

        out_raw = (options.get("out") or "").strip()
        if out_raw:
            out_path = Path(out_raw).expanduser().resolve()
        else:
            ext = "json.gz" if fmt == "gz" else "zip"
            out_path = (data_dir / "bundles" / f"bundle_{user.username}.{ext}").resolve()

        out_path.parent.mkdir(parents=True, exist_ok=True)

        progress_mode = (options.get("progress") or "auto").strip().lower()
        if progress_mode not in {"auto", "on", "off"}:
            progress_mode = "auto"

        out_stream = raw_stream_for_command_stdout(self.stdout)
        progress = ProgressLine(
            out_stream,
            enabled=(progress_mode != "off"),
            force=(progress_mode == "on"),
        )
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

        # Compact JSON to keep bundles small.
        raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

        if fmt == "gz":
            with gzip.open(out_path, "wb", compresslevel=9) as f:
                f.write(raw)
        else:
            # Write a zip that contains:
            # - review_bundle.json.gz (the same JSON payload as before)
            # - Luganda.dic (source dictionary text)
            with ZipFile(out_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as z:
                z.writestr("review_bundle.json.gz", gzip.compress(raw, compresslevel=9))
                z.write(dic_path, arcname="Luganda.dic")

        self.stdout.write(
            self.style.SUCCESS(
                "Bundle written: "
                f"{out_path} (stems={payload.get('summary', {}).get('stems')}, tasks={payload.get('summary', {}).get('tasks')}, examples={payload.get('summary', {}).get('examples')})"
            )
        )
