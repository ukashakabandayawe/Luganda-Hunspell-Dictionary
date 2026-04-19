from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
	dependencies = [
		("review", "0004_alter_flag_group"),
	]

	operations = [
		migrations.CreateModel(
			name="StemGroup",
			fields=[
				("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
				("title", models.CharField(max_length=255)),
				("source_line_no", models.IntegerField(db_index=True, unique=True)),
			],
		),
		migrations.AddField(
			model_name="stem",
			name="group",
			field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="stems", to="review.stemgroup"),
		),
	]
