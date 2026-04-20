from django.db import migrations, models
from django.db.models import F


def forwards_copy_description_to_aff_description(apps, schema_editor):
	Flag = apps.get_model("review", "Flag")
	# Preserve current behavior on upgrade: existing Flag.description values were
	# historically sourced from Luganda.aff comments. Copy them into the new
	# auto-synced field so exports keep showing descriptions until you edit the
	# reviewer-friendly description in Admin.
	Flag.objects.filter(aff_description="").exclude(description="").update(aff_description=F("description"))


class Migration(migrations.Migration):
	dependencies = [
		("review", "0005_stem_group"),
	]

	operations = [
		migrations.AddField(
			model_name="flag",
			name="aff_description",
			field=models.TextField(blank=True, default=""),
		),
		migrations.RunPython(forwards_copy_description_to_aff_description, migrations.RunPython.noop),
	]
