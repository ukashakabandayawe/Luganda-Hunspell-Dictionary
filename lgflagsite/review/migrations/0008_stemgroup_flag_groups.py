from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		("review", "0007_stemgroup_title_unique"),
	]

	operations = [
		migrations.AddField(
			model_name="stemgroup",
			name="flag_groups",
			field=models.JSONField(blank=True, default=list),
		),
	]
