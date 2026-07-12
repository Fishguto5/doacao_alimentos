from django.contrib import admin

from core.models import (
    Alimento,
    Avaliacao,
    Categoria,
    Doacao,
    Notificacao,
    SolicitacaoDoacao,
    Usuario,
)

admin.site.register(Usuario)
admin.site.register(Categoria)
admin.site.register(Doacao)
admin.site.register(Alimento)
admin.site.register(SolicitacaoDoacao)
admin.site.register(Notificacao)
admin.site.register(Avaliacao)
