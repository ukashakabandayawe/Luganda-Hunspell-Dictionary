from __future__ import annotations

from pathlib import Path
import re
import shutil
from typing import Dict, Set, Tuple

from django.conf import settings
from django.db.models import QuerySet
from django.contrib.auth import get_user_model

from .dic_io import apply_flags_to_dic_file, ensure_working_dic_exists, rebuild_working_dic
from .hunspell import detect_flag_mode
from .models import StemFlagTask


def _default_paths() -> tuple[Path, Path]:
	aff_path = Path(getattr(settings, "HUNSPELL_AFF_PATH"))
	source_dic = Path(getattr(settings, "HUNSPELL_DIC_SOURCE_PATH"))
	return aff_path, source_dic


def working_dic_path_for_user_id(user_id: int) -> Path:
	"""Return the per-user working .dic path.

	We prefer username-based folder names for readability:
	  WORKING_DIR/users/<username>/Luganda.dic

	For backward compatibility, if a legacy id-based path exists:
	  WORKING_DIR/users/<id>/Luganda.dic
	we will migrate it to the username-based path (best-effort).
	"""

	if not user_id:
		raise ValueError("user_id is required")

	working_dir = Path(getattr(settings, "WORKING_DIR"))
	legacy = working_dir / "users" / str(int(user_id)) / "Luganda.dic"

	User = get_user_model()
	user = User.objects.filter(id=int(user_id)).only("id", "username").first()
	username = (user.username if user else f"user_{int(user_id)}") or f"user_{int(user_id)}"

	# Make it safe for Windows paths.
	safe = re.sub(r"[^A-Za-z0-9._-]+", "_", username).strip("._-") or f"user_{int(user_id)}"
	preferred = working_dir / "users" / safe / "Luganda.dic"

	# If legacy exists and preferred doesn't, migrate.
	try:
		if legacy.exists() and not preferred.exists():
			preferred.parent.mkdir(parents=True, exist_ok=True)
			shutil.move(str(legacy), str(preferred))
			# Move lock file too if present.
			legacy_lock = Path(str(legacy) + ".lock")
			preferred_lock = Path(str(preferred) + ".lock")
			if legacy_lock.exists() and not preferred_lock.exists():
				shutil.move(str(legacy_lock), str(preferred_lock))
			# Clean up empty legacy dir if possible.
			try:
				legacy.parent.rmdir()
			except OSError:
				pass
	except Exception:
		# Best-effort migration only.
		pass

	# Prefer the readable path.
	if preferred.exists() or not legacy.exists():
		return preferred
	return legacy


def build_approved_flags_map(tasks: QuerySet[StemFlagTask]) -> Dict[str, Set[str]]:
	out: Dict[str, Set[str]] = {}
	for t in tasks.select_related("stem", "flag"):
		if t.status != StemFlagTask.Status.APPROVED:
			continue
		stem = t.stem.text
		out.setdefault(stem, set()).add(t.flag.code)
	return out


def rebuild_working_dic_for_user_id(user_id: int) -> Tuple[int, int]:
	"""Rebuild a user's working .dic from source using that user's approved tasks.

	This is important on hosts with ephemeral filesystems: even if the working file
	gets deleted, we can regenerate it from persisted review decisions.
	"""
	aff_path, source_dic = _default_paths()
	working_dic = working_dic_path_for_user_id(user_id)
	flag_mode = detect_flag_mode(aff_path)
	approved_map = build_approved_flags_map(
		StemFlagTask.objects.filter(
			decided_by_id=user_id,
		)
	)
	total_matched, total_changed, _, _ = rebuild_working_dic(
		source_dic,
		working_dic,
		approved_map,
		flag_mode,
	)
	return total_matched, total_changed


def update_working_dic_for_task_change(
	task: StemFlagTask,
	previous_status: str,
	new_status: str,
	*,
	acting_user_id: int,
) -> Tuple[int, int]:
	"""Keep a per-user working .dic in sync with approvals.

	- Approve: incrementally apply that flag to that stem in that user's working .dic.
	- Un-approve (approved -> rejected/skipped/pending): rebuild that user's working .dic from source using approvals decided by that user.
	"""
	aff_path, source_dic = _default_paths()
	working_dic = working_dic_path_for_user_id(acting_user_id)
	flag_mode = detect_flag_mode(aff_path)

	existed_before = working_dic.exists()
	ensure_working_dic_exists(source_dic, working_dic)

	if new_status == StemFlagTask.Status.APPROVED:
		# If the working file didn't exist (e.g. after a redeploy), rebuild from DB
		# approvals first so we don't lose historical approvals.
		if not existed_before:
			return rebuild_working_dic_for_user_id(acting_user_id)

		# Incremental apply.
		stem = task.stem.text
		total_matched, total_changed, _, _ = apply_flags_to_dic_file(
			working_dic,
			{stem: {task.flag.code}},
			flag_mode,
		)
		return total_matched, total_changed

	if previous_status == StemFlagTask.Status.APPROVED and new_status != StemFlagTask.Status.APPROVED:
		# Need to remove previously applied flags, so rebuild from scratch.
		return rebuild_working_dic_for_user_id(acting_user_id)

	return 0, 0
