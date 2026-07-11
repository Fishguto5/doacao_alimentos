from django.contrib.auth.hashers import identify_hasher, make_password
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
from core.services import recompute_doacao_derivados
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
    def _hash_password(self, password):
        try:
            identify_hasher(password)
            return password
        except ValueError:
            return make_password(password)

    def create(self, validated_data):
        validated_data["password"] = self._hash_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = self._hash_password(validated_data["password"])
        return super().update(instance, validated_data)

    class Meta:
        model = Usuario
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}


class AuthLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


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
        read_only_fields = [
            "expira_em",
            "estimativa_peso",
            "concluida_por_doador",
            "concluida_por_receptor",
        ]


class SolicitacaoDoacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitacaoDoacao
        fields = "__all__"


class AlimentoSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        unidade = attrs.get("unidade", getattr(instance, "unidade", None))
        quantidade = attrs.get("quantidade", getattr(instance, "quantidade", None))

        if quantidade is not None and unidade is not None:
            if quantidade <= 0:
                raise ValidationError({"quantidade": "A quantidade deve ser maior que zero."})

            if unidade == "unidade":
                if quantidade % 1 != 0:
                    raise ValidationError({"quantidade": "A quantidade para a unidade 'unidade' deve ser um número inteiro."})
                if quantidade > 100:
                    raise ValidationError({"quantidade": "A quantidade máxima para 'unidade' é 100."})
            elif unidade in {"kg", "l"}:
                if quantidade > 100:
                    raise ValidationError({"quantidade": f"A quantidade máxima para '{unidade}' é 100."})
            elif unidade in {"g", "ml"}:
                if quantidade % 1 != 0:
                    raise ValidationError({"quantidade": f"A quantidade para '{unidade}' deve ser um número inteiro."})
                if quantidade < 50:
                    raise ValidationError({"quantidade": f"A quantidade mínima para '{unidade}' é 50."})
                if quantidade > 999:
                    raise ValidationError({"quantidade": f"A quantidade máxima para '{unidade}' é 999. Para 1000 ou mais, use a unidade superior correspondente."})

        return attrs

    def create(self, validated_data):
        alimento = super().create(validated_data)
        recompute_doacao_derivados(alimento.doacao)
        return alimento

    def update(self, instance, validated_data):
        doacao_anterior = instance.doacao
        alimento = super().update(instance, validated_data)
        recompute_doacao_derivados(alimento.doacao)
        if alimento.doacao_id != doacao_anterior.id:
            recompute_doacao_derivados(doacao_anterior)
        return alimento

    class Meta:
        model = Alimento
        fields = "__all__"


class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = "__all__"


class AvaliacaoSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        doacao = attrs.get("doacao", getattr(instance, "doacao", None))
        avaliador = attrs.get("avaliador", getattr(instance, "avaliador", None))
        avaliado = attrs.get("avaliado", getattr(instance, "avaliado", None))

        if not doacao or not avaliador or not avaliado:
            return attrs

        if doacao.status != DoacaoStatus.CONCLUIDA:
            raise ValidationError(
                {"doacao": "A doacao precisa estar concluida para receber avaliacoes."}
            )

        if avaliador.id != doacao.receptor_id:
            raise ValidationError(
                {"avaliador": "Somente o usuario que recebeu a doacao pode avaliar."}
            )

        if avaliado.id != doacao.doador_id:
            raise ValidationError(
                {"avaliado": "A avaliacao deve ser feita para o doador da doacao."}
            )

        return attrs

    class Meta:
        model = Avaliacao
        fields = "__all__"
