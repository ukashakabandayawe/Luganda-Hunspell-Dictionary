from django.db import migrations, models


def merge_duplicate_stem_groups(apps, schema_editor):
	StemGroup = apps.get_model("review", "StemGroup")
	Stem = apps.get_model("review", "Stem")

	# Find duplicate titles.
	# Note: keep this migration lightweight; avoid importing Django ORM aggregates directly.
	titles = (
		StemGroup.objects.values_list("title", flat=True)
		.order_by("title")
		.distinct()
	)

	for title in titles:
		groups = list(StemGroup.objects.filter(title=title).order_by("source_line_no", "id"))
		if len(groups) <= 1:
			continue

		# Choose canonical group: prefer the one with most stems, then earliest source_line_no.
		best = None
		best_key = None
		for g in groups:
			stem_count = Stem.objects.filter(group_id=g.id).count()
			line_no = int(getattr(g, "source_line_no", 0) or 0)
			key = (-stem_count, line_no, int(g.id))
			if best is None or key < best_key:
				best = g
				best_key = key
		canonical = best
		if canonical is None:
			continue

		# Keep earliest line number across duplicates for stable ordering.
		earliest_line = min(int(getattr(g, "source_line_no", 0) or 0) for g in groups)
		if int(getattr(canonical, "source_line_no", 0) or 0) != int(earliest_line):
			StemGroup.objects.filter(id=canonical.id).update(source_line_no=earliest_line)

		# Repoint stems to canonical and delete the rest.
		for g in groups:
			if int(g.id) == int(canonical.id):
				continue
			Stem.objects.filter(group_id=g.id).update(group_id=canonical.id)
			StemGroup.objects.filter(id=g.id).delete()


class Migration(migrations.Migration):
	dependencies = [
		("review", "0006_flag_aff_description"),
	]

	operations = [
		# source_line_no is for ordering, not identity.
		migrations.AlterField(
			model_name="stemgroup",
			name="source_line_no",
			field=models.IntegerField(db_index=True),
		),
		# Merge existing duplicates before adding unique constraint.
		migrations.RunPython(merge_duplicate_stem_groups, migrations.RunPython.noop),
		# Make title the identity key.
		migrations.AlterField(
			model_name="stemgroup",
			name="title",
			field=models.CharField(max_length=255, unique=True),
		),
	]
