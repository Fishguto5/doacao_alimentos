"""Cria notificações a partir dos eventos reais das doações."""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.models import (
    Avaliacao,
    Doacao,
    DoacaoStatus,
    MensagemChat,
    Notificacao,
    SolicitacaoDoacao,
    SolicitacaoStatus,
)


def _notify(usuario_id, doacao, mensagem):
    usuario_id = getattr(usuario_id, "pk", usuario_id)
    if usuario_id:
        Notificacao.objects.create(
            usuario_id=usuario_id, doacao=doacao, mensagem=mensagem
        )


@receiver(pre_save, sender=Doacao)
def remember_donation_status(sender, instance, raw=False, **kwargs):
    if not raw and instance.pk:
        instance._previous_status = (
            sender.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        )


@receiver(post_save, sender=Doacao)
def notify_donation(sender, instance, created, raw=False, **kwargs):
    if raw:
        return
    if created:
        _notify(instance.doador_id, instance, f'Sua doação "{instance.titulo}" foi criada.')
    elif (
        instance._previous_status == DoacaoStatus.DISPONIVEL
        and instance.status == DoacaoStatus.RESERVADA
    ):
        _notify(instance.doador_id, instance, f'Sua doação "{instance.titulo}" foi reservada.')
        if instance.receptor_id != instance.doador_id:
            _notify(instance.receptor_id, instance, f'Sua reserva da doação "{instance.titulo}" foi confirmada.')


@receiver(post_save, sender=SolicitacaoDoacao)
def notify_new_request(sender, instance, created, raw=False, **kwargs):
    if raw or not created or instance.status != SolicitacaoStatus.PENDENTE:
        return
    if instance.solicitante_id and instance.solicitante_id != instance.doacao.doador_id:
        _notify(
            instance.doacao.doador_id,
            instance.doacao,
            f'Nova solicitação de {instance.solicitante.nome} para a doação "{instance.doacao.titulo}".',
        )


@receiver(post_save, sender=MensagemChat)
def notify_chat_message(sender, instance, created, raw=False, **kwargs):
    if raw or not created or not instance.remetente_id:
        return
    doacao = instance.doacao
    destinatario_id = (
        doacao.receptor_id if instance.remetente_id == doacao.doador_id else doacao.doador_id
    )
    if destinatario_id != instance.remetente_id:
        _notify(destinatario_id, doacao, f'Nova mensagem de {instance.remetente.nome} sobre "{doacao.titulo}".')


@receiver(post_save, sender=Avaliacao)
def notify_rating(sender, instance, created, raw=False, **kwargs):
    if raw or not created or instance.avaliado_id == instance.avaliador_id:
        return
    _notify(
        instance.avaliado_id,
        instance.doacao,
        f'{instance.avaliador.nome} avaliou você na doação "{instance.doacao.titulo}".',
    )
