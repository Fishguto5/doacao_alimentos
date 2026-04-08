from django.db import migrations, models

CATEGORIAS_INICIAIS = [
    "Graos e cereais",
    "Massas",
    "Enlatados",
    "Farinhas",
    "Leguminosas",
    "Leite e derivados",
    "Proteinas",
    "Hortifruti",
    "Temperos e condimentos",
    "Bebidas",
    "Infantil",
    "Higiene e limpeza",
]


def popular_categorias(apps, schema_editor):
    Categoria = apps.get_model("core", "Categoria")
    for nome in CATEGORIAS_INICIAIS:
        Categoria.objects.get_or_create(nome=nome)


def remover_categorias_populadas(apps, schema_editor):
    Categoria = apps.get_model("core", "Categoria")
    Categoria.objects.filter(nome__in=CATEGORIAS_INICIAIS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_usuario_endereco_campos"),
    ]

    operations = [
        migrations.AddField(
            model_name="doacao",
            name="complemento",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name="doacao",
            name="concluida_por_doador",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="doacao",
            name="concluida_por_receptor",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="doacao",
            name="logradouro",
            field=models.CharField(default="", max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="doacao",
            name="numero",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="doacao",
            name="expira_em",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(popular_categorias, remover_categorias_populadas),
    ]
