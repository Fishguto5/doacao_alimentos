"""
Testes para funcionalidade de upload de imagem em doações.
"""

import io
import uuid

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from core.models import Doacao, Usuario


@pytest.fixture
def api_client():
    return APIClient()


def _create_usuario(seed: str, prefix: str) -> Usuario:
    """Helper para criar um usuário de teste."""
    return Usuario.objects.create(
        nome=f"{prefix} {seed}",
        email=f"{prefix.lower()}_{seed}@example.com",
        password="senha12345",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua Teste",
        numero="100",
        complemento="",
        foto_perfil_url="https://example.com/perfil.jpg",
    )


def _create_test_image(name="test.jpg", size=(100, 100), format="JPEG"):
    """Helper para criar uma imagem de teste."""
    image = Image.new("RGB", size, color="red")
    image_io = io.BytesIO()
    image.save(image_io, format=format)
    image_io.seek(0)
    return SimpleUploadedFile(name, image_io.getvalue(), content_type=f"image/{format.lower()}")


@pytest.mark.django_db
def test_criar_doacao_com_imagem(api_client):
    """Teste: criar doação com imagem válida."""
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    imagem = _create_test_image("doacao.jpg")

    response = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "titulo": f"Doacao com Imagem {seed}",
            "descricao": "Teste upload de imagem",
            "imagem": imagem,
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua Teste",
            "numero": "100",
            "complemento": "",
            "estimativa_peso": "5.00",
        },
        format="multipart",
    )

    assert response.status_code == 201
    assert response.data["data"]["imagem"] is not None
    assert "media/doacoes" in response.data["data"]["imagem"]

    # Verificar que a doação foi criada com a imagem
    doacao = Doacao.objects.get(id=response.data["data"]["id"])
    assert doacao.imagem is not None
    assert doacao.imagem.name.startswith("doacoes/")


@pytest.mark.django_db
def test_criar_doacao_sem_imagem(api_client):
    """Teste: criar doação sem imagem (campo é opcional)."""
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    response = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "titulo": f"Doacao sem Imagem {seed}",
            "descricao": "Teste sem upload de imagem",
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua Teste",
            "numero": "100",
            "complemento": "",
            "estimativa_peso": "5.00",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["data"]["imagem"] == "" or response.data["data"]["imagem"] is None


def _create_padded_image(name, size_in_bytes):
    """
    Helper para criar uma imagem PNG perfeitamente válida estruturalmente, 
    mas com o tamanho exato de bytes especificado (usando preenchimento).
    """
    image = Image.new("RGB", (1, 1), color="red")
    image_io = io.BytesIO()
    image.save(image_io, format="PNG")
    png_bytes = image_io.getvalue()
    
    padding_needed = size_in_bytes - len(png_bytes)
    if padding_needed > 0:
        png_bytes = png_bytes + b"\x00" * padding_needed
    
    return SimpleUploadedFile(name, png_bytes, content_type="image/png")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "tamanho_bytes, expected_status, cenario_info",
    [
        # --- PARTICIONAMENTO EM CLASSES DE EQUIVALÊNCIA (PCE) & ANÁLISE DE VALOR LIMITE (AVL) ---
        # A classe de equivalência válida aceita imagens com tamanho <= 5 MB (5.242.880 bytes)
        # A classe de equivalência inválida rejeita imagens com tamanho > 5 MB (5.242.880 bytes)
        
        # 1. Classe Válida (PCE) - Imagem Pequena comum
        (100 * 1024, 201, "Imagem comum de 100KB (Classe Válida)"),

        # 2. Limite Superior Válido (AVL - T)
        (5 * 1024 * 1024, 201, "Imagem exatamente no limite de 5MB (Limite Superior Exato Válido)"),

        # 3. Limite Superior Inválido (AVL - T + 1 byte)
        (5 * 1024 * 1024 + 1, 400, "Imagem com 5MB + 1 byte (Limite Superior Externo Inválido)"),
    ],
)
def test_validacao_tamanho_maximo_imagem(api_client, tamanho_bytes, expected_status, cenario_info):
    """
    TÉCNICA DE TESTE: ANÁLISE DE VALOR LIMITE (AVL) & CLASSES DE EQUIVALÊNCIA (PCE)
    Unidade sob Teste: DoacaoSerializer.validate_imagem (tamanho máximo de imagem)
    
    Valida se a API do backend rejeita imagens com tamanho de arquivo estritamente maior
    que 5MB na fronteira exata de bytes.
    """
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    imagem = _create_padded_image("doacao.png", tamanho_bytes)

    response = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "titulo": f"Doacao Imagem {seed}",
            "descricao": f"Teste de upload: {cenario_info}",
            "imagem": imagem,
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua Teste",
            "numero": "100",
            "complemento": "",
            "estimativa_peso": "5.00",
        },
        format="multipart",
    )

    assert response.status_code == expected_status, f"Falha no cenário: {cenario_info}"
    if expected_status == 400:
        assert "imagem" in response.data, "Deveria conter uma mensagem de erro de validação para o campo 'imagem'."


@pytest.mark.django_db
def test_validacao_tipos_imagem_validos(api_client):
    """Teste: diferentes tipos de imagem são aceitos."""
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    # Testar diferentes formatos
    for formato in ["JPEG", "PNG", "GIF"]:
        imagem = _create_test_image(f"test.{formato.lower()}", format=formato)

        response = api_client.post(
            "/doacao/",
            data={
                "doador": doador.id,
                "titulo": f"Doacao {formato} {seed}",
                "descricao": f"Teste {formato}",
                "imagem": imagem,
                "status": "disponivel",
                "cep": "13000000",
                "cidade": "Campinas",
                "estado": "SP",
                "bairro": "Centro",
                "logradouro": "Rua Teste",
                "numero": "100",
                "complemento": "",
                "estimativa_peso": "5.00",
            },
            format="multipart",
        )

        assert response.status_code == 201
        assert response.data["data"]["imagem"] is not None


@pytest.mark.django_db
def test_atualizar_doacao_com_nova_imagem(api_client):
    """Teste: atualizar uma doação substituindo a imagem."""
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    imagem1 = _create_test_image("imagem1.jpg")

    # Criar doação com primeira imagem
    create_response = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "titulo": f"Doacao Update {seed}",
            "descricao": "Teste atualização de imagem",
            "imagem": imagem1,
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua Teste",
            "numero": "100",
            "complemento": "",
            "estimativa_peso": "5.00",
        },
        format="multipart",
    )

    assert create_response.status_code == 201
    doacao_id = create_response.data["data"]["id"]
    primeira_imagem = create_response.data["data"]["imagem"]

    # Atualizar com nova imagem
    imagem2 = _create_test_image("imagem2.jpg")
    update_response = api_client.put(
        "/doacao/",
        data={
            "id": doacao_id,
            "doador": doador.id,
            "titulo": f"Doacao Update Modificada {seed}",
            "descricao": "Teste atualização de imagem - nova imagem",
            "imagem": imagem2,
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua Teste",
            "numero": "100",
            "complemento": "",
            "estimativa_peso": "5.00",
        },
        format="multipart",
    )

    assert update_response.status_code == 200
    assert update_response.data["data"]["imagem"] is not None
    # A imagem deve ser diferente da anterior
    assert update_response.data["data"]["imagem"] != primeira_imagem


@pytest.mark.django_db
def test_obter_doacao_com_imagem_em_get(api_client):
    """Teste: ao obter uma doação, a URL da imagem é retornada."""
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    imagem = _create_test_image("doacao.jpg")

    # Criar doação com imagem
    create_response = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "titulo": f"Doacao Get {seed}",
            "descricao": "Teste GET de doação com imagem",
            "imagem": imagem,
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua Teste",
            "numero": "100",
            "complemento": "",
            "estimativa_peso": "5.00",
        },
        format="multipart",
    )

    doacao_id = create_response.data["data"]["id"]

    # Obter doação
    get_response = api_client.get(f"/doacao/{doacao_id}/", format="json")

    assert get_response.status_code == 200
    assert get_response.data["data"]["imagem"] is not None
    assert "media/doacoes" in get_response.data["data"]["imagem"]


@pytest.mark.django_db
def test_listar_doacoes_com_imagens(api_client):
    """Teste: listar todas as doações retorna as URLs das imagens."""
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    # Criar duas doações, uma com e uma sem imagem
    imagem = _create_test_image("doacao.jpg")

    api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "titulo": f"Doacao Com Imagem {seed}",
            "descricao": "Com imagem",
            "imagem": imagem,
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua Teste",
            "numero": "100",
            "complemento": "",
            "estimativa_peso": "5.00",
        },
        format="multipart",
    )

    api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "titulo": f"Doacao Sem Imagem {seed}",
            "descricao": "Sem imagem",
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua Teste",
            "numero": "100",
            "complemento": "",
            "estimativa_peso": "5.00",
        },
        format="json",
    )

    # Listar todas as doações
    list_response = api_client.get("/doacao/", format="json")

    assert list_response.status_code == 200
    assert len(list_response.data["data"]) >= 2

    # Verificar que pelo menos uma tem imagem
    doacoes_com_imagem = [d for d in list_response.data["data"] if d.get("imagem")]
    assert len(doacoes_com_imagem) >= 1
