from django.db import migrations, models


class Migration(migrations.Migration):
	dependencies = [
		("review", "0002_flag_group"),
	]

	operations = [
		migrations.AddField(
			model_name="flag",
			name="aff_order",
			field=models.PositiveIntegerField(db_index=True, default=1000000),
		),
	]
