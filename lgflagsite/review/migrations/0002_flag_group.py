from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="flag",
            name="group",
            field=models.CharField(
                choices=[
                    ("priority", "Priority"),
                    ("nouns", "Nouns"),
                    ("adjectives", "Adjectives"),
                    ("advanced", "Advanced flags"),
                ],
                default="priority",
                max_length=16,
            ),
        ),
    ]
