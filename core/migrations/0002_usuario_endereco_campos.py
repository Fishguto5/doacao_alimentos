from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='complemento',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='usuario',
            name='logradouro',
            field=models.CharField(default='', max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usuario',
            name='numero',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
