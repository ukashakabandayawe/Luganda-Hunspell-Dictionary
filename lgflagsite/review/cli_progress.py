from __future__ import annotations

import sys
import time
from typing import Callable, TextIO


def raw_stream_for_command_stdout(command_stdout) -> TextIO:
	"""Return a raw stream suitable for in-place terminal updates.

	Django's BaseCommand.stdout is usually an OutputWrapper that appends newlines.
	We want the underlying stream so '\r' updates overwrite a single line.
	"""
	return getattr(command_stdout, "_out", None) or sys.stdout


class ProgressLine:
	"""Very small progress helper (no external deps).

	- Uses carriage-return updates to keep progress on a single line.
	- Enables ANSI blue bar only when stream is a TTY.
	- If stream is not a TTY, only enables progress when explicitly forced.
	"""

	def __init__(self, stream: TextIO, *, enabled: bool = True, force: bool = False, width: int = 26):
		self.stream = stream
		self._is_tty = bool(getattr(stream, "isatty", lambda: False)())
		self.enabled = bool(enabled) and (self._is_tty or bool(force))
		self._last_len = 0
		self._last_ts = 0.0
		self._use_color = self._is_tty
		self._width = int(width) if int(width) > 0 else 26

	def write(self, text: str, *, force: bool = True) -> None:
		if not self.enabled:
			return

		now = time.time()
		min_interval = 0.10
		if not force and (now - self._last_ts) < min_interval:
			return
		self._last_ts = now

		s = str(text)
		try:
			pad = max(0, self._last_len - len(s))
			self._last_len = len(s)
			self.stream.write("\r" + s + (" " * pad))
			self.stream.flush()
		except Exception:
			self.enabled = False

	def render(self, *, prefix: str, done: int, total: int, extra: str = "") -> str:
		total_i = int(total) if int(total) > 0 else 1
		done_i = max(0, min(int(done), total_i))
		pct = int(round((done_i / total_i) * 100.0))

		filled = int(round((done_i / total_i) * self._width))
		if filled < 0:
			filled = 0
		if filled > self._width:
			filled = self._width

		bar = ("█" * filled) + ("░" * (self._width - filled))
		if self._use_color:
			bar = "\x1b[34m" + bar + "\x1b[0m"

		pfx = (str(prefix).strip() + " ") if str(prefix).strip() else ""
		sfx = ("  " + str(extra).strip()) if str(extra).strip() else ""
		return f"{pfx}{pct:3d}% |{bar}| {done_i}/{total_i}{sfx}"

	def render_bytes(self, *, prefix: str, done_bytes: int, total_bytes: int, extra: str = "") -> str:
		total_b = int(total_bytes) if int(total_bytes) > 0 else 1
		done_b = max(0, min(int(done_bytes), total_b))
		return self.render(prefix=prefix, done=done_b, total=total_b, extra=self._fmt_bytes_pair(done_b, total_b, extra=extra))

	def callback_counts(self, *, prefix: str = "") -> Callable[[int, int, int, int], None]:
		def _cb(done_stems: int, total_stems: int, tasks: int, examples: int) -> None:
			extra = f"tasks={int(tasks)}  examples={int(examples)}"
			self.write(self.render(prefix=prefix, done=done_stems, total=total_stems, extra=extra), force=False)

		return _cb

	def finish(self) -> None:
		if not self.enabled:
			return
		try:
			self.stream.write("\n")
			self.stream.flush()
		except Exception:
			pass

	@staticmethod
	def _fmt_bytes(n: int) -> str:
		n = int(n)
		if n >= 1024 * 1024 * 1024:
			return f"{n / (1024 * 1024 * 1024):.1f}GB"
		if n >= 1024 * 1024:
			return f"{n / (1024 * 1024):.1f}MB"
		if n >= 1024:
			return f"{n / 1024:.1f}KB"
		return f"{n}B"

	@classmethod
	def _fmt_bytes_pair(cls, done_b: int, total_b: int, *, extra: str = "") -> str:
		base = f"{cls._fmt_bytes(done_b)}/{cls._fmt_bytes(total_b)}"
		if str(extra).strip():
			return base + "  " + str(extra).strip()
		return base
