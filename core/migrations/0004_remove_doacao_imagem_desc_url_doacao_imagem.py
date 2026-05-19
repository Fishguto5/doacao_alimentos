from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_doacao_endereco_expiracao_conclusao_e_categorias"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="doacao",
            name="imagem_desc_url",
        ),
        migrations.AddField(
            model_name="doacao",
            name="imagem",
            field=models.ImageField(blank=True, null=True, upload_to="doacoes/%Y/%m/%d/"),
        ),
    ]
