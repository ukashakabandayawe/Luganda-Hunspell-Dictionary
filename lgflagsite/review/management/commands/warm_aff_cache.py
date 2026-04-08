from __future__ import annotations

import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Warm in-process caches for Hunspell .aff parsing (improves first-review latency)."

    def handle(self, *args, **options):
        from review.hunspell import _aff_signature, _affix_block_ranges_cached, _detect_flag_mode_cached

        aff_path = Path(getattr(settings, "HUNSPELL_AFF_PATH"))
        sig = _aff_signature(aff_path)

        self.stdout.write(f"Warming .aff cache for: {aff_path}")
        t0 = time.perf_counter()
        mode = _detect_flag_mode_cached(*sig)
        idx = _affix_block_ranges_cached(*sig)
        dt = (time.perf_counter() - t0) * 1000

        self.stdout.write(f"Detected FLAG mode: {mode}")
        self.stdout.write(f"Indexed flags: {len(idx)}")
        self.stdout.write(self.style.SUCCESS(f"Done in {dt:.1f}ms"))
