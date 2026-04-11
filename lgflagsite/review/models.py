from django.conf import settings
from django.db import models
from django.utils import timezone


class Flag(models.Model):
	class Group(models.TextChoices):
		PRIORITY = "priority", "Priority"
		NOUNS = "nouns", "Nouns"
		ADJECTIVES = "adjectives", "Adjectives"
		REFLEXIVE_VERBS = "reflexive_verbs", "Reflexive verbs"
		ADVANCED = "advanced", "Advanced flags"

	code = models.CharField(max_length=8, unique=True)
	# Hunspell affix type: 'P' (prefix), 'S' (suffix), or '' when unknown.
	affix_type = models.CharField(max_length=1, blank=True, default="")
	# The 1-based order the flag first appears in Luganda.aff (used for admin sorting).
	# Defaults high so unknown/un-synced flags appear last until synced.
	aff_order = models.PositiveIntegerField(default=1_000_000, db_index=True)
	description = models.TextField(blank=True, default="")
	is_active = models.BooleanField(default=True)
	group = models.CharField(max_length=16, choices=Group.choices, default=Group.PRIORITY)

	def __str__(self) -> str:
		return self.code


class Stem(models.Model):
	text = models.CharField(max_length=255, unique=True)
	# Raw flags string from Luganda.dic (after '/', before whitespace).
	flags_raw = models.CharField(max_length=512, blank=True, default="")
	# Preserve everything after the first whitespace so export can round-trip.
	trailing = models.TextField(blank=True, default="")
	# Ordering from the source dictionary import (1-based line number).
	source_line_no = models.IntegerField(default=0)

	assigned_to = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="assigned_stems",
	)
	assigned_at = models.DateTimeField(null=True, blank=True)

	def __str__(self) -> str:
		return self.text


class StemFlagTask(models.Model):
	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		APPROVED = "approved", "Approved"
		REJECTED = "rejected", "Rejected"
		SKIPPED = "skipped", "Skipped"

	stem = models.ForeignKey(Stem, on_delete=models.CASCADE, related_name="flag_tasks")
	flag = models.ForeignKey(Flag, on_delete=models.CASCADE, related_name="stem_tasks")

	status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
	updated_at = models.DateTimeField(auto_now=True)
	decided_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="decisions_latest",
	)
	decided_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		unique_together = [("stem", "flag")]

	def __str__(self) -> str:
		return f"{self.stem.text} -> {self.flag.code} ({self.status})"

	def set_status(self, status: str, user, note: str = "", decided_at=None):
		self.status = status
		self.decided_by = user
		self.decided_at = decided_at or timezone.now()
		self.save(update_fields=["status", "decided_by", "decided_at", "updated_at"])
		ReviewDecision.objects.create(task=self, user=user, decision=status, note=note or "")


class ReviewDecision(models.Model):
	task = models.ForeignKey(StemFlagTask, on_delete=models.CASCADE, related_name="decision_log")
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	decision = models.CharField(max_length=16)
	note = models.TextField(blank=True, default="")
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self) -> str:
		who = self.user.username if self.user else "(deleted user)"
		return f"{who}: {self.task.stem.text}/{self.task.flag.code} -> {self.decision}"
