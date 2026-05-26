from abc import ABC

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from core.models import Doacao, DoacaoStatus


class DoacaoState(ABC):
    def reservar(self, doacao: Doacao, receptor_id: int | None = None) -> Doacao:
        raise ValidationError({"status": "Esta doação não pode ser reservada neste estado."})

    def concluir(self, doacao: Doacao, usuario_id: int) -> Doacao:
        raise ValidationError({"status": "Esta doação não pode ser concluída neste estado."})

    def cancelar(self, doacao: Doacao) -> Doacao:
        raise ValidationError({"status": "Esta doação não pode ser cancelada neste estado."})

    def expirar(self, doacao: Doacao) -> Doacao:
        raise ValidationError({"status": "Esta doação não pode expirar neste estado."})


class DisponivelState(DoacaoState):
    def reservar(self, doacao: Doacao, receptor_id: int | None = None) -> Doacao:
        if receptor_id is None and doacao.receptor_id is None:
            raise ValidationError({"receptor": "Informe o receptor para reservar a doação."})

        if receptor_id is not None:
            doacao.receptor_id = receptor_id

        doacao.status = DoacaoStatus.RESERVADA
        doacao.data_reserva = timezone.now()
        doacao.concluida_por_doador = False
        doacao.concluida_por_receptor = False
        doacao.data_conclusao = None
        doacao.save(
            update_fields=[
                "status",
                "receptor",
                "data_reserva",
                "concluida_por_doador",
                "concluida_por_receptor",
                "data_conclusao",
                "updated_at",
            ]
        )
        return doacao

    def cancelar(self, doacao: Doacao) -> Doacao:
        doacao.status = DoacaoStatus.CANCELADA
        doacao.save(update_fields=["status", "updated_at"])
        return doacao


class ReservadaState(DoacaoState):
    def concluir(self, doacao: Doacao, usuario_id: int) -> Doacao:
        if usuario_id not in {doacao.doador_id, doacao.receptor_id}:
            raise ValidationError(
                {
                    "confirmacao_usuario_id": (
                        "O usuário informado precisa ser o doador ou o receptor da doação."
                    )
                }
            )

        if usuario_id == doacao.doador_id:
            doacao.concluida_por_doador = True
        else:
            doacao.concluida_por_receptor = True

        update_fields = ["concluida_por_doador", "concluida_por_receptor", "updated_at"]

        if doacao.concluida_por_doador and doacao.concluida_por_receptor:
            doacao.status = DoacaoStatus.CONCLUIDA
            doacao.data_conclusao = timezone.now()
            update_fields.extend(["status", "data_conclusao"])

        doacao.save(update_fields=update_fields)
        return doacao

    def cancelar(self, doacao: Doacao) -> Doacao:
        doacao.status = DoacaoStatus.CANCELADA
        doacao.save(update_fields=["status", "updated_at"])
        return doacao

    def expirar(self, doacao: Doacao) -> Doacao:
        doacao.status = DoacaoStatus.EXPIRADA
        doacao.save(update_fields=["status", "updated_at"])
        return doacao


class ConcluidaState(DoacaoState):
    pass


class ExpiradaState(DoacaoState):
    pass


class CanceladaState(DoacaoState):
    pass


def get_doacao_state(doacao: Doacao) -> DoacaoState:
    if doacao.status == DoacaoStatus.DISPONIVEL:
        return DisponivelState()
    if doacao.status == DoacaoStatus.RESERVADA:
        return ReservadaState()
    if doacao.status == DoacaoStatus.CONCLUIDA:
        return ConcluidaState()
    if doacao.status == DoacaoStatus.EXPIRADA:
        return ExpiradaState()
    if doacao.status == DoacaoStatus.CANCELADA:
        return CanceladaState()
    raise ValidationError({"status": "Status de doação desconhecido."})


def reservar_doacao(doacao: Doacao, receptor_id: int | None = None) -> Doacao:
    return get_doacao_state(doacao).reservar(doacao, receptor_id)


def concluir_doacao(doacao: Doacao, usuario_id: int) -> Doacao:
    return get_doacao_state(doacao).concluir(doacao, usuario_id)


def cancelar_doacao(doacao: Doacao) -> Doacao:
    return get_doacao_state(doacao).cancelar(doacao)


def expirar_doacao(doacao: Doacao) -> Doacao:
    return get_doacao_state(doacao).expirar(doacao)
