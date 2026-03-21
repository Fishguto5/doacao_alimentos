from django.db import models

'''

'''
class Doacao(models.Model):
    doador = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    receptor = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)

    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    imagem_desc_url = models.URLField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default='disponivel')
    data_publicacao = models.DateTimeField(auto_now_add=True)
    data_reserva = models.DateTimeField(null=True, blank=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    cep = models.CharField(max_length=20)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    expira_em = models.DateTimeField(null=True, blank=True)

    estimativa_peso = models.FloatField(null=True, blank=True)
    receptor_aceitou = models.BooleanField(default=False)
    doador_aceitou = models.BooleanField(default=False)


class Alimento(models.Model):
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True)
    doacao = models.ForeignKey('Doacao', on_delete=models.SET_NULL, null=True)

    nome = models.CharField(max_length=100)
    data_validade = models.DateField()
    quantidade = models.FloatField()
    unidade = models.CharField(max_length=20, default='unidade')


class Notificacao(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    mensagem = models.TextField()
    status = models.CharField(max_length=20, default='pendente')
    timestamp = models.DateTimeField(auto_now_add=True)


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    cep = models.CharField(max_length=20)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    foto_perfil_url = models.URLField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

class Avaliacao(models.Model):
    doacao = models.ForeignKey(Doacao, on_delete=models.CASCADE)
    avaliador = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    avaliado = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    nota = models.IntegerField()
    comentario = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    