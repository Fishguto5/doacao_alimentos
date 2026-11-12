from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_delete_person"),
    ]

    operations = [
        migrations.AlterField(
            model_name="doacao",
            name="imagem",
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
