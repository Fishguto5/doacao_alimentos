from django.utils import timezone

from core.models import Doacao, DoacaoStatus


def recompute_doacao_expiracao(doacao: Doacao) -> Doacao:
    """Define expira_em como o menor data_validade dos alimentos da doacao."""
    menor_validade = (
        doacao.alimentos.exclude(data_validade__isnull=True)
        .order_by("data_validade")
        .values_list("data_validade", flat=True)
        .first()
    )
    doacao.expira_em = menor_validade
    doacao.save(update_fields=["expira_em", "updated_at"])
    return doacao


def marcar_doacao_concluida_por_doador(doacao: Doacao) -> Doacao:
    """Marca conclusao por voto do doador e conclui doacao quando criterio e atendido."""
    doacao.concluida_por_doador = True
    doacao.save(update_fields=["concluida_por_doador", "updated_at"])

    # Fluxo atual: para concluir, basta confirmacao do doador.
    if doacao.status == DoacaoStatus.RESERVADA and doacao.concluida_por_doador:
        doacao.status = DoacaoStatus.CONCLUIDA
        doacao.data_conclusao = timezone.now()
        doacao.save(update_fields=["status", "data_conclusao", "updated_at"])

    return doacao
