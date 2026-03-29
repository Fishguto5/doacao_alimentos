from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# classe teste para testar POST, PUT, GET etc


class Person(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField(default=18)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class DoacaoStatus(models.TextChoices):
    DISPONIVEL = "disponivel", "Disponivel"
    RESERVADA = "reservada", "Reservada"
    CONCLUIDA = "concluida", "Concluida"
    EXPIRADA = "expirada", "Expirada"
    CANCELADA = "cancelada", "Cancelada"


class SolicitacaoStatus(models.TextChoices):
    PENDENTE = "pendente", "Pendente"
    ACEITA = "aceita", "Aceita"
    RECUSADA = "recusada", "Recusada"
    CANCELADA = "cancelada", "Cancelada"


class NotificacaoStatus(models.TextChoices):
    PENDENTE = "pendente", "Pendente"
    LIDA = "lida", "Lida"


class UnidadeMedida(models.TextChoices):
    UNIDADE = "unidade", "Unidade"
    KG = "kg", "Kg"
    G = "g", "G"
    L = "l", "L"
    ML = "ml", "Ml"


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    cep = models.CharField(max_length=20)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    logradouro = models.CharField(max_length=150)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=150, blank=True)
    foto_perfil_url = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Ordenar por cidade, estado para facilitar buscas por localização
    class Meta:
        indexes = [
            models.Index(fields=["cidade", "estado"]),
        ]

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Doacao(models.Model):
    # Facilita buscas por doador através de algo como:
    # usuario.doacoes_criadas.all()
    # O comportamento de models.SET_NULL pode causar situações de checagem se uma doação
    # tem ou não um doador associado, mas é importante para manter o histórico de doações
    # models.CASCADE deletaria tudo.
    doador = models.ForeignKey(
        "Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doacoes_criadas",
    )
    # Facilita buscas por receptor através de algo como:
    # usuario.doacoes_recebidas.all()
    receptor = models.ForeignKey(
        "Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doacoes_recebidas",
    )
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    imagem_desc_url = models.URLField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20,
        choices=DoacaoStatus.choices,
        default=DoacaoStatus.DISPONIVEL,
        db_index=True,
    )
    data_publicacao = models.DateTimeField(auto_now_add=True)
    data_reserva = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    cep = models.CharField(max_length=20)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    expira_em = models.DateTimeField(null=True, blank=True)
    estimativa_peso = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            # Para ajudar com buscas do tipo:
            # Doacao.objects.filter(status='disponivel').order_by('data_publicacao')
            models.Index(fields=["status", "data_publicacao"]),
            # Para ajudar com buscas por localização e status, como:
            # Doacao.objects.filter(cidade='São Paulo', estado='SP', status='disponivel')
            models.Index(fields=["cidade", "estado", "status"]),
            # Para ajudar com buscas por doador e status, como:
            # Doacao.objects.filter(doador=usuario, status='disponivel')
            models.Index(fields=["doador", "status"]),
        ]

    def __str__(self):
        return self.titulo


class SolicitacaoDoacao(models.Model):
    doacao = models.ForeignKey(
        "Doacao",
        on_delete=models.CASCADE,
        related_name="solicitacoes",
    )
    solicitante = models.ForeignKey(
        "Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="solicitacoes_enviadas",
    )
    status = models.CharField(
        max_length=20,
        choices=SolicitacaoStatus.choices,
        default=SolicitacaoStatus.PENDENTE,
        db_index=True,
    )
    mensagem = models.TextField(blank=True)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_resposta = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doacao", "solicitante"],
                name="unique_solicitacao_por_usuario_e_doacao",
            ),
        ]
        indexes = [
            models.Index(fields=["doacao", "status"]),
            models.Index(fields=["solicitante", "status"]),
        ]

    def __str__(self):
        return f"{self.solicitante} -> {self.doacao}"


class Alimento(models.Model):
    categoria = models.ForeignKey(
        "Categoria",
        on_delete=models.PROTECT,
        related_name="alimentos",
    )
    doacao = models.ForeignKey(
        "Doacao",
        on_delete=models.CASCADE,
        related_name="alimentos",
    )
    nome = models.CharField(max_length=100)
    data_validade = models.DateField(null=True, blank=True)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    unidade = models.CharField(
        max_length=20,
        choices=UnidadeMedida.choices,
        default=UnidadeMedida.UNIDADE,
    )

    class Meta:
        indexes = [
            models.Index(fields=["doacao"]),
            models.Index(fields=["categoria"]),
        ]

    def __str__(self):
        return self.nome


class Notificacao(models.Model):
    usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        related_name="notificacoes",
    )
    doacao = models.ForeignKey(
        "Doacao",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notificacoes",
    )
    mensagem = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=NotificacaoStatus.choices,
        default=NotificacaoStatus.PENDENTE,
        db_index=True,
    )
    lida_em = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["usuario", "status", "created_at"]),
        ]

    def __str__(self):
        return f"Notificacao para {self.usuario}"


class Avaliacao(models.Model):
    doacao = models.ForeignKey(
        "Doacao",
        on_delete=models.CASCADE,
        related_name="avaliacoes",
    )
    avaliador = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        related_name="avaliacoes_feitas",
    )
    avaliado = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        related_name="avaliacoes_recebidas",
    )
    nota = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comentario = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Um avaliador só pode avaliar uma doação uma vez, para evitar avaliações duplicadas
            models.UniqueConstraint(
                fields=["doacao", "avaliador"],
                name="unique_avaliacao_por_doacao_e_avaliador",
            ),
            # O avaliador não pode avaliar a si mesmo
            models.CheckConstraint(
                condition=~models.Q(avaliador=models.F("avaliado")),
                name="avaliador_diferente_de_avaliado",
            ),
            # Uma avaliação recebe nota entre 1 e 5
            models.CheckConstraint(
                condition=models.Q(nota__gte=1) & models.Q(nota__lte=5),
                name="nota_entre_1_e_5",
            ),
        ]
        indexes = [
            models.Index(fields=["avaliado"]),
            models.Index(fields=["doacao"]),
        ]

    def __str__(self):
        return f"{self.avaliador} -> {self.avaliado} ({self.nota})"
