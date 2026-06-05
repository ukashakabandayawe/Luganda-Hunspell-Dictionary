from __future__ import annotations

import gzip
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from django.conf import settings

from .hunspell import generate_examples_for_flag, get_flag_description
from .models import Stem, StemFlagTask


def _allowed_flag_groups_for_stem(stem: Stem) -> set[str] | None:
	g = getattr(stem, "group", None)
	if g is None:
		return None
	try:
		raw = list(getattr(g, "flag_groups", None) or [])
	except Exception:
		raw = []
	allowed = {str(x).strip() for x in raw if str(x).strip()}
	return allowed or None


def _utc_now_iso() -> str:
	return datetime.now(timezone.utc).isoformat()


def build_offline_review_bundle_payload(
	*,
	user,
	limit_examples: int = 120,
	examples_for: str = "pending",
	progress_callback: Optional[Callable[[int, int, int, int], None]] = None,
) -> dict:
	"""Build the JSON payload for the offline Android review bundle.

	Returns a dict that can be JSON-serialized.
	"""
	limit_examples = int(limit_examples)
	if limit_examples < 0:
		raise ValueError("limit_examples must be >= 0")

	examples_for = (examples_for or "pending").strip().lower()
	if examples_for not in {"pending", "all"}:
		raise ValueError("examples_for must be 'pending' or 'all'")

	repo_dir = Path(getattr(settings, "REPO_DIR"))
	data_dir = Path(getattr(settings, "DATA_DIR"))
	aff_path = Path(getattr(settings, "HUNSPELL_AFF_PATH")).resolve()

	if not aff_path.exists():
		raise FileNotFoundError(f"Hunspell .aff not found: {aff_path}")

	stems = list(
		Stem.objects.filter(assigned_to=user)
		.select_related("group")
		.only(
			"id",
			"text",
			"source_line_no",
			"group__id",
			"group__title",
			"group__source_line_no",
		)
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
	total_stems = len(stems)
	for stem_i, s in enumerate(stems, start=1):
		task_rows = []
		allowed = _allowed_flag_groups_for_stem(s)
		for t in tasks_by_stem.get(s.id, []):
			if allowed is not None and getattr(getattr(t, "flag", None), "group", None) not in allowed:
				continue
			total_tasks += 1
			code = t.flag.code
			desc = t.flag.description or t.flag.aff_description or get_flag_description(aff_path, code) or ""

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
				"group": (
					{
						"id": int(s.group.id),
						"title": s.group.title,
						"source_line_no": int(s.group.source_line_no or 0),
					}
					if getattr(s, "group", None) is not None
					else None
				),
				"tasks": task_rows,
			}
		)

		if progress_callback is not None:
			# (done_stems, total_stems, total_tasks_so_far, total_examples_so_far)
			progress_callback(stem_i, total_stems, total_tasks, total_examples)

	return {
		"schema": 1,
		"generated_at": _utc_now_iso(),
		"repo_dir": str(repo_dir),
		"data_dir": str(data_dir),
		"user": {"id": int(user.id), "username": getattr(user, "username", str(user.id))},
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


def encode_bundle_payload_gz(payload: dict) -> bytes:
	"""Encode payload as compact JSON, gzip-compressed."""
	raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
	return gzip.compress(raw, compresslevel=9)
