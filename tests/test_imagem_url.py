import pytest
from rest_framework.test import APIClient

from core.models import Doacao, Usuario


@pytest.mark.django_db
def test_criar_doacao_com_url_de_imagem():
    client = APIClient()
    usuario = Usuario.objects.create(
        nome="Doador",
        email="doador@example.com",
        password="senha123",
        cep="01000000",
        cidade="São Paulo",
        estado="SP",
        bairro="Centro",
        logradouro="Rua A",
        numero="1",
    )
    payload = {
        "doador": usuario.id,
        "titulo": "Cesta básica",
        "descricao": "Alimentos não perecíveis",
        "imagem": "https://example.com/cesta.jpg",
        "status": "disponivel",
        "cep": "01000000",
        "cidade": "São Paulo",
        "estado": "SP",
        "bairro": "Centro",
        "logradouro": "Rua A",
        "numero": "1",
    }

    response = client.post("/doacao/", payload, format="json")

    assert response.status_code == 201
    assert response.data["data"]["imagem"] == payload["imagem"]
    assert Doacao.objects.get(id=response.data["data"]["id"]).imagem == payload["imagem"]


@pytest.mark.django_db
def test_criar_doacao_sem_url_de_imagem():
    client = APIClient()
    usuario = Usuario.objects.create(
        nome="Doador",
        email="doador-sem-imagem@example.com",
        password="senha123",
        cep="01000000",
        cidade="São Paulo",
        estado="SP",
        bairro="Centro",
        logradouro="Rua A",
        numero="1",
    )
    payload = {
        "doador": usuario.id,
        "titulo": "Cesta básica",
        "descricao": "Sem imagem",
        "status": "disponivel",
        "cep": "01000000",
        "cidade": "São Paulo",
        "estado": "SP",
        "bairro": "Centro",
        "logradouro": "Rua A",
        "numero": "1",
    }

    response = client.post("/doacao/", payload, format="json")

    assert response.status_code == 201
    assert response.data["data"]["imagem"] == ""
