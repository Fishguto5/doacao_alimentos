from decimal import ROUND_HALF_UP, Decimal

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.models import Doacao, DoacaoStatus, UnidadeMedida


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


def _quantidade_em_kg(quantidade: Decimal, unidade: str) -> Decimal:
    if unidade == UnidadeMedida.KG:
        return quantidade
    if unidade == UnidadeMedida.G:
        return quantidade / Decimal("1000")
    if unidade == UnidadeMedida.L:
        return quantidade
    if unidade == UnidadeMedida.ML:
        return quantidade / Decimal("1000")
    return Decimal("0")


def recompute_doacao_estimativa_peso(doacao: Doacao) -> Doacao:
    """Define estimativa_peso em kg a partir das quantidades dos alimentos."""
    total = Decimal("0")
    for quantidade, unidade in doacao.alimentos.values_list("quantidade", "unidade"):
        total += _quantidade_em_kg(quantidade, unidade)

    doacao.estimativa_peso = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    doacao.save(update_fields=["estimativa_peso", "updated_at"])
    return doacao


def recompute_doacao_derivados(doacao: Doacao) -> Doacao:
    recompute_doacao_expiracao(doacao)
    return recompute_doacao_estimativa_peso(doacao)


def registrar_voto_conclusao(doacao: Doacao, usuario_id: int) -> Doacao:
    """Registra voto de conclusao e conclui a doacao quando ambas as partes votam."""
    if doacao.status != DoacaoStatus.RESERVADA:
        raise ValidationError(
            {"status": "A doacao precisa estar reservada antes de receber votos de conclusao."}
        )

    if usuario_id == doacao.doador_id:
        doacao.concluida_por_doador = True
    elif usuario_id == doacao.receptor_id:
        doacao.concluida_por_receptor = True
    else:
        raise ValidationError(
            {
                "confirmacao_usuario_id": (
                    "O usuario informado precisa ser o doador ou o receptor da doacao."
                )
            }
        )

    update_fields = ["concluida_por_doador", "concluida_por_receptor", "updated_at"]

    if doacao.concluida_por_doador and doacao.concluida_por_receptor:
        doacao.status = DoacaoStatus.CONCLUIDA
        doacao.data_conclusao = timezone.now()
        update_fields.extend(["status", "data_conclusao"])

    doacao.save(update_fields=update_fields)
    return doacao
