from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import (
    Alimento,
    Avaliacao,
    Categoria,
    Doacao,
    DoacaoStatus,
    Notificacao,
    Person,
    SolicitacaoDoacao,
    Usuario,
)
from core.services import recompute_doacao_expiracao
from core.state_machine import (
    cancelar_doacao,
    concluir_doacao,
    expirar_doacao,
    reservar_doacao,
)

# serializer irá transformar os dados de uma "forma" para outra.
# Por exemplo, de um modelo de banco para um json.


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class DoacaoSerializer(serializers.ModelSerializer):
    confirmacao_usuario_id = serializers.IntegerField(write_only=True, required=False)

    def validate_imagem(self, value):
        """Validar tamanho máximo da imagem (5MB)"""
        if value:
            file_size = value.size
            limit_mb = 5
            if file_size > limit_mb * 1024 * 1024:
                raise ValidationError(
                    f"Tamanho máximo da imagem é {limit_mb}MB. "
                    f"Tamanho atual: {file_size / (1024 * 1024):.2f}MB"
                )
        return value

    def validate(self, attrs):
        status = attrs.get("status")
        if status == DoacaoStatus.CONCLUIDA:
            instance = getattr(self, "instance", None)
            if instance and instance.status != DoacaoStatus.RESERVADA:
                raise ValidationError(
                    {"status": "A doacao precisa estar reservada antes de ser concluida."}
                )
            if attrs.get("confirmacao_usuario_id") is None:
                raise ValidationError(
                    {
                        "confirmacao_usuario_id": (
                            "Informe o usuario que esta confirmando a conclusao da doacao."
                        )
                    }
                )
        return attrs

    def update(self, instance, validated_data):
        status = validated_data.get("status")
        confirmacao_usuario_id = validated_data.pop("confirmacao_usuario_id", None)

        # Evita que clientes alterem flags de voto diretamente.
        validated_data.pop("concluida_por_doador", None)
        validated_data.pop("concluida_por_receptor", None)

        if status in {
            DoacaoStatus.RESERVADA,
            DoacaoStatus.CONCLUIDA,
            DoacaoStatus.CANCELADA,
            DoacaoStatus.EXPIRADA,
        }:
            validated_data.pop("status", None)

        if status == DoacaoStatus.CONCLUIDA:
            # A transição para concluída depende da votação bilateral.
            validated_data.pop("data_conclusao", None)

        doacao = super().update(instance, validated_data)

        if status == DoacaoStatus.RESERVADA:
            doacao = reservar_doacao(doacao, receptor_id=validated_data.get("receptor"))
        elif status == DoacaoStatus.CONCLUIDA:
            doacao = concluir_doacao(doacao, confirmacao_usuario_id)
        elif status == DoacaoStatus.CANCELADA:
            doacao = cancelar_doacao(doacao)
        elif status == DoacaoStatus.EXPIRADA:
            doacao = expirar_doacao(doacao)

        return doacao

    class Meta:
        model = Doacao
        fields = "__all__"
        read_only_fields = ["expira_em", "concluida_por_doador", "concluida_por_receptor"]


class SolicitacaoDoacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoDoacao
        fields = "__all__"


class AlimentoSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        alimento = super().create(validated_data)
        recompute_doacao_expiracao(alimento.doacao)
        return alimento

    def update(self, instance, validated_data):
        doacao_anterior = instance.doacao
        alimento = super().update(instance, validated_data)
        recompute_doacao_expiracao(alimento.doacao)
        if alimento.doacao_id != doacao_anterior.id:
            recompute_doacao_expiracao(doacao_anterior)
        return alimento

    class Meta:
        model = Alimento
        fields = "__all__"


class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = "__all__"


class AvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = "__all__"
