import uuid

import pytest
from rest_framework.test import APIClient

from core.models import (
    Alimento,
    Avaliacao,
    Categoria,
    Doacao,
    Notificacao,
    Person,
    SolicitacaoDoacao,
    Usuario,
)

RESOURCE_MODEL_MAP = {
    "person": Person,
    "usuario": Usuario,
    "categoria": Categoria,
    "doacao": Doacao,
    "solicitacao-doacao": SolicitacaoDoacao,
    "alimento": Alimento,
    "notificacao": Notificacao,
    "avaliacao": Avaliacao,
}


@pytest.fixture
def api_client():
    return APIClient()


def _create_usuario(seed: str, prefix: str) -> Usuario:
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


def _create_dependencies(resource: str, seed: str) -> dict:
    dependencies = {}

    if resource in {"doacao", "solicitacao-doacao", "alimento", "notificacao", "avaliacao"}:
        dependencies["doador"] = _create_usuario(seed, "Doador")
        dependencies["receptor"] = _create_usuario(seed, "Receptor")

    if resource in {"solicitacao-doacao", "alimento", "notificacao", "avaliacao"}:
        dependencies["categoria"] = Categoria.objects.create(nome=f"Categoria {seed}")
        dependencies["doacao"] = Doacao.objects.create(
            doador=dependencies["doador"],
            receptor=dependencies["receptor"],
            titulo=f"Doacao Base {seed}",
            descricao="Doacao criada para testes",
            status="disponivel",
            cep="13000000",
            cidade="Campinas",
            estado="SP",
            bairro="Centro",
            logradouro="Rua Teste",
            numero="100",
            complemento="",
            estimativa_peso="8.00",
        )

    return dependencies


def _payloads_for(resource: str, dependencies: dict, seed: str) -> tuple[dict, dict, dict]:
    if resource == "person":
        create_payload = {
            "name": f"Pessoa {seed}",
            "age": 25,
            "city": "Campinas",
        }
        put_payload = {
            "name": f"Pessoa Atualizada {seed}",
            "age": 26,
            "city": "Valinhos",
        }
        patch_payload = {"city": "Sumare"}
        return create_payload, put_payload, patch_payload

    if resource == "usuario":
        create_payload = {
            "nome": f"Usuario {seed}",
            "email": f"usuario_{seed}@example.com",
            "password": "senha12345",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua A",
            "foto_perfil_url": "https://example.com/usuario.jpg",
        }
        put_payload = {
            "nome": f"Usuario Atualizado {seed}",
            "email": f"usuario_atualizado_{seed}@example.com",
            "password": "senha67890",
            "cep": "13100000",
            "cidade": "Valinhos",
            "estado": "SP",
            "bairro": "Jardim",
            "logradouro": "Rua B",
            "foto_perfil_url": "https://example.com/usuario2.jpg",
        }
        patch_payload = {"bairro": "Centro Novo"}
        return create_payload, put_payload, patch_payload

    if resource == "categoria":
        create_payload = {"nome": f"Categoria API {seed}"}
        put_payload = {"nome": f"Categoria Atualizada {seed}"}
        patch_payload = {"nome": f"Categoria Parcial {seed}"}
        return create_payload, put_payload, patch_payload

    if resource == "doacao":
        create_payload = {
            "doador": dependencies["doador"].id,
            "receptor": dependencies["receptor"].id,
            "titulo": f"Doacao {seed}",
            "descricao": "Descricao inicial",
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua Teste",
            "numero": "100",
            "complemento": "Casa",
            "estimativa_peso": "10.50",
        }
        put_payload = {
            "doador": dependencies["doador"].id,
            "receptor": dependencies["receptor"].id,
            "titulo": f"Doacao Atualizada {seed}",
            "descricao": "Descricao atualizada",
            "status": "reservada",
            "cep": "13100000",
            "cidade": "Valinhos",
            "estado": "SP",
            "bairro": "Jardim",
            "logradouro": "Rua B",
            "numero": "200",
            "complemento": "Apto 4",
            "estimativa_peso": "11.00",
        }
        patch_payload = {"descricao": "Descricao parcial"}
        return create_payload, put_payload, patch_payload

    if resource == "solicitacao-doacao":
        create_payload = {
            "doacao": dependencies["doacao"].id,
            "solicitante": dependencies["receptor"].id,
            "status": "pendente",
            "mensagem": f"Solicitacao inicial {seed}",
        }
        put_payload = {
            "doacao": dependencies["doacao"].id,
            "solicitante": dependencies["receptor"].id,
            "status": "aceita",
            "mensagem": f"Solicitacao atualizada {seed}",
        }
        patch_payload = {"status": "recusada"}
        return create_payload, put_payload, patch_payload

    if resource == "alimento":
        create_payload = {
            "categoria": dependencies["categoria"].id,
            "doacao": dependencies["doacao"].id,
            "nome": f"Arroz {seed}",
            "data_validade": "2026-12-31",
            "quantidade": "5.00",
            "unidade": "kg",
        }
        put_payload = {
            "categoria": dependencies["categoria"].id,
            "doacao": dependencies["doacao"].id,
            "nome": f"Arroz Integral {seed}",
            "data_validade": "2027-01-31",
            "quantidade": "6.00",
            "unidade": "kg",
        }
        patch_payload = {"quantidade": "3.00"}
        return create_payload, put_payload, patch_payload

    if resource == "notificacao":
        create_payload = {
            "usuario": dependencies["receptor"].id,
            "doacao": dependencies["doacao"].id,
            "mensagem": f"Notificacao inicial {seed}",
            "status": "pendente",
        }
        put_payload = {
            "usuario": dependencies["receptor"].id,
            "doacao": dependencies["doacao"].id,
            "mensagem": f"Notificacao atualizada {seed}",
            "status": "lida",
        }
        patch_payload = {"status": "lida"}
        return create_payload, put_payload, patch_payload

    if resource == "avaliacao":
        create_payload = {
            "doacao": dependencies["doacao"].id,
            "avaliador": dependencies["doador"].id,
            "avaliado": dependencies["receptor"].id,
            "nota": 4,
            "comentario": f"Avaliacao inicial {seed}",
        }
        put_payload = {
            "doacao": dependencies["doacao"].id,
            "avaliador": dependencies["doador"].id,
            "avaliado": dependencies["receptor"].id,
            "nota": 5,
            "comentario": f"Avaliacao atualizada {seed}",
        }
        patch_payload = {"nota": 3}
        return create_payload, put_payload, patch_payload

    raise ValueError(f"Recurso nao suportado: {resource}")


def _assert_put_field(resource: str, response_data: dict, put_payload: dict) -> None:
    key_map = {
        "person": "name",
        "usuario": "nome",
        "categoria": "nome",
        "doacao": "titulo",
        "solicitacao-doacao": "status",
        "alimento": "nome",
        "notificacao": "mensagem",
        "avaliacao": "nota",
    }
    field = key_map[resource]
    assert response_data[field] == put_payload[field]


def _assert_patch_field(resource: str, response_data: dict, patch_payload: dict) -> None:
    field = next(iter(patch_payload.keys()))
    expected = patch_payload[field]
    if field == "quantidade":
        expected = "3.00"
    assert response_data[field] == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "resource",
    [
        "person",
        "usuario",
        "categoria",
        "doacao",
        "solicitacao-doacao",
        "alimento",
        "notificacao",
        "avaliacao",
    ],
)
def test_resource_crud_full_cycle(api_client, resource):
    # Setup
    seed = uuid.uuid4().hex[:8]
    dependencies = _create_dependencies(resource, seed)
    create_payload, put_payload_no_id, patch_payload_no_id = _payloads_for(
        resource, dependencies, seed
    )
    list_url = f"/{resource}/"

    # Run - GET collection
    list_response = api_client.get(list_url, format="json")
    assert list_response.status_code == 200
    assert isinstance(list_response.data["data"], list)

    # Run - POST create
    post_response = api_client.post(list_url, data=create_payload, format="json")
    assert post_response.status_code == 201
    created_id = post_response.data["data"]["id"]
    model_class = RESOURCE_MODEL_MAP[resource]
    assert model_class.objects.filter(pk=created_id).exists()

    # Run - GET detail
    detail_url = f"/{resource}/{created_id}/"
    detail_response = api_client.get(detail_url, format="json")
    assert detail_response.status_code == 200
    assert detail_response.data["data"]["id"] == created_id

    # Run - PUT full update
    put_payload = {"id": created_id, **put_payload_no_id}
    put_response = api_client.put(list_url, data=put_payload, format="json")
    assert put_response.status_code == 200
    _assert_put_field(resource, put_response.data["data"], put_payload_no_id)

    # Run - PATCH partial update
    patch_payload = {"id": created_id, **patch_payload_no_id}
    patch_response = api_client.patch(list_url, data=patch_payload, format="json")
    assert patch_response.status_code == 200
    _assert_patch_field(resource, patch_response.data["data"], patch_payload_no_id)

    # Run - DELETE
    delete_response = api_client.delete(detail_url, format="json")
    assert delete_response.status_code == 204

    # Teardown assertion
    assert not model_class.objects.filter(pk=created_id).exists()


@pytest.mark.django_db
def test_doacao_expira_em_e_definida_pela_menor_data_validade(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    categoria = Categoria.objects.create(nome=f"Categoria Vencimento {seed}")

    resp_doacao = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "receptor": None,
            "titulo": f"Doacao Validade {seed}",
            "descricao": "Teste de validade",
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua A",
            "numero": "10",
            "complemento": "",
            "estimativa_peso": "4.00",
        },
        format="json",
    )
    assert resp_doacao.status_code == 201
    doacao_id = resp_doacao.data["data"]["id"]

    for nome, validade in [("Arroz", "2026-12-10"), ("Feijao", "2026-10-01")]:
        resp_alimento = api_client.post(
            "/alimento/",
            data={
                "categoria": categoria.id,
                "doacao": doacao_id,
                "nome": nome,
                "data_validade": validade,
                "quantidade": "1.00",
                "unidade": "kg",
            },
            format="json",
        )
        assert resp_alimento.status_code == 201

    detail = api_client.get(f"/doacao/{doacao_id}/", format="json")
    assert detail.status_code == 200
    assert detail.data["data"]["expira_em"] == "2026-10-01"


@pytest.mark.django_db
def test_doacao_so_conclui_quando_reservada(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    create_resp = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "receptor": None,
            "titulo": f"Doacao Conclusao {seed}",
            "descricao": "Teste conclusao",
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua B",
            "numero": "20",
            "complemento": "",
            "estimativa_peso": "2.00",
        },
        format="json",
    )
    assert create_resp.status_code == 201
    doacao_id = create_resp.data["data"]["id"]

    conclude_resp = api_client.patch(
        "/doacao/",
        data={
            "id": doacao_id,
            "status": "concluida",
            "confirmacao_usuario_id": doador.id,
        },
        format="json",
    )
    assert conclude_resp.status_code == 400
    assert "status" in conclude_resp.data


@pytest.mark.django_db
def test_doacao_conclui_apos_voto_de_doador_e_receptor(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    receptor = _create_usuario(seed, "Receptor")

    create_resp = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "receptor": receptor.id,
            "titulo": f"Doacao Votacao {seed}",
            "descricao": "Teste votacao",
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua C",
            "numero": "30",
            "complemento": "",
            "estimativa_peso": "3.00",
        },
        format="json",
    )
    assert create_resp.status_code == 201
    doacao_id = create_resp.data["data"]["id"]

    reservar_resp = api_client.patch(
        "/doacao/",
        data={"id": doacao_id, "status": "reservada", "receptor": receptor.id},
        format="json",
    )
    assert reservar_resp.status_code == 200

    voto_doador = api_client.patch(
        "/doacao/",
        data={
            "id": doacao_id,
            "status": "concluida",
            "confirmacao_usuario_id": doador.id,
        },
        format="json",
    )
    assert voto_doador.status_code == 200
    assert voto_doador.data["data"]["status"] == "reservada"
    assert voto_doador.data["data"]["concluida_por_doador"] is True
    assert voto_doador.data["data"]["concluida_por_receptor"] is False

    voto_receptor = api_client.patch(
        "/doacao/",
        data={
            "id": doacao_id,
            "status": "concluida",
            "confirmacao_usuario_id": receptor.id,
        },
        format="json",
    )
    assert voto_receptor.status_code == 200
    assert voto_receptor.data["data"]["status"] == "concluida"
    assert voto_receptor.data["data"]["concluida_por_doador"] is True
    assert voto_receptor.data["data"]["concluida_por_receptor"] is True
    assert voto_receptor.data["data"]["data_conclusao"] is not None


@pytest.mark.django_db
def test_doacao_reserva_apenas_quando_disponivel(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    receptor = _create_usuario(seed, "Receptor")

    create_resp = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "receptor": None,
            "titulo": f"Doacao Reserva {seed}",
            "descricao": "Teste reserva",
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua D",
            "numero": "40",
            "complemento": "",
            "estimativa_peso": "2.00",
        },
        format="json",
    )
    assert create_resp.status_code == 201
    doacao_id = create_resp.data["data"]["id"]

    reservar_resp = api_client.patch(
        "/doacao/",
        data={
            "id": doacao_id,
            "status": "reservada",
            "receptor": receptor.id,
        },
        format="json",
    )
    assert reservar_resp.status_code == 200
    assert reservar_resp.data["data"]["status"] == "reservada"
    assert reservar_resp.data["data"]["receptor"] == receptor.id
    assert reservar_resp.data["data"]["data_reserva"] is not None


@pytest.mark.django_db
def test_doacao_nao_pode_ser_reservada_quando_ja_reservada(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    receptor = _create_usuario(seed, "Receptor")

    create_resp = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "receptor": receptor.id,
            "titulo": f"Doacao Reservada {seed}",
            "descricao": "Teste reserva invalida",
            "status": "reservada",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua E",
            "numero": "50",
            "complemento": "",
            "estimativa_peso": "3.00",
        },
        format="json",
    )
    assert create_resp.status_code == 201
    doacao_id = create_resp.data["data"]["id"]

    reservar_novamente_resp = api_client.patch(
        "/doacao/",
        data={
            "id": doacao_id,
            "status": "reservada",
        },
        format="json",
    )
    assert reservar_novamente_resp.status_code == 400
    assert "status" in reservar_novamente_resp.data


@pytest.mark.django_db
def test_listagem_de_doacoes_pode_filtrar_por_categoria(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    categoria_frutas = Categoria.objects.create(nome=f"Frutas {seed}")
    categoria_legumes = Categoria.objects.create(nome=f"Legumes {seed}")

    doacao_frutas = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Frutas {seed}",
        descricao="Doacao com frutas",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua F",
        numero="10",
        complemento="",
        estimativa_peso="2.00",
    )
    doacao_mista = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Mista {seed}",
        descricao="Doacao com itens de categorias diferentes",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua M",
        numero="20",
        complemento="",
        estimativa_peso="3.00",
    )
    doacao_legumes = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Legumes {seed}",
        descricao="Doacao com legumes",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua L",
        numero="30",
        complemento="",
        estimativa_peso="4.00",
    )

    Alimento.objects.create(
        categoria=categoria_frutas,
        doacao=doacao_frutas,
        nome=f"Banana {seed}",
        data_validade="2026-12-10",
        quantidade="1.00",
        unidade="kg",
    )
    Alimento.objects.create(
        categoria=categoria_frutas,
        doacao=doacao_mista,
        nome=f"Maca {seed}",
        data_validade="2026-12-11",
        quantidade="1.00",
        unidade="kg",
    )
    Alimento.objects.create(
        categoria=categoria_frutas,
        doacao=doacao_mista,
        nome=f"Uva {seed}",
        data_validade="2026-12-12",
        quantidade="1.00",
        unidade="kg",
    )
    Alimento.objects.create(
        categoria=categoria_legumes,
        doacao=doacao_legumes,
        nome=f"Cenoura {seed}",
        data_validade="2026-12-13",
        quantidade="1.00",
        unidade="kg",
    )

    response = api_client.get(f"/doacao/?categoria={categoria_frutas.id}", format="json")

    assert response.status_code == 200
    ids = {item["id"] for item in response.data["data"]}
    assert ids == {doacao_frutas.id, doacao_mista.id}


@pytest.mark.django_db
def test_listagem_de_doacoes_pode_filtrar_por_status(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    doacao_disponivel = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Disponivel {seed}",
        descricao="Doacao ainda disponivel",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua D",
        numero="10",
        complemento="",
        estimativa_peso="2.00",
    )
    doacao_reservada = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Reservada {seed}",
        descricao="Doacao ja reservada",
        status="reservada",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua R",
        numero="20",
        complemento="",
        estimativa_peso="3.00",
    )
    Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Cancelada {seed}",
        descricao="Doacao cancelada",
        status="cancelada",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua C",
        numero="30",
        complemento="",
        estimativa_peso="4.00",
    )

    response = api_client.get("/doacao/?status=disponivel", format="json")

    assert response.status_code == 200
    ids = {item["id"] for item in response.data["data"]}
    assert ids == {doacao_disponivel.id}

    response_reservada = api_client.get("/doacao/?status=reservada", format="json")

    assert response_reservada.status_code == 200
    ids_reservada = {item["id"] for item in response_reservada.data["data"]}
    assert ids_reservada == {doacao_reservada.id}


@pytest.mark.django_db
def test_listagem_de_doacoes_rejeita_status_invalido(api_client):
    response = api_client.get("/doacao/?status=nao_existe", format="json")

    assert response.status_code == 400
    assert "msg" in response.data


@pytest.mark.django_db
def test_listagem_de_doacoes_pode_filtrar_por_peso_maximo(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    doacao_leve = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Leve {seed}",
        descricao="Doacao com peso baixo",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua P",
        numero="40",
        complemento="",
        estimativa_peso="4.50",
    )
    doacao_media = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Media {seed}",
        descricao="Doacao com peso intermediario",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua Q",
        numero="50",
        complemento="",
        estimativa_peso="9.00",
    )
    doacao_pesada = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Pesada {seed}",
        descricao="Doacao com peso alto",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua R",
        numero="60",
        complemento="",
        estimativa_peso="14.00",
    )

    response = api_client.get("/doacao/?peso_max=15", format="json")

    assert response.status_code == 200
    ids = {item["id"] for item in response.data["data"]}
    assert ids == {doacao_leve.id, doacao_media.id, doacao_pesada.id}


@pytest.mark.django_db
def test_listagem_de_doacoes_pode_filtrar_por_validade_minima(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    doacao_valida = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Valida {seed}",
        descricao="Validade futura",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua A",
        numero="10",
        complemento="",
        estimativa_peso="2.00",
        expira_em="2030-12-31",
    )
    doacao_proxima = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Proxima {seed}",
        descricao="Validade proxima",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua B",
        numero="20",
        complemento="",
        estimativa_peso="3.00",
        expira_em="2027-01-15",
    )
    Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Expirada {seed}",
        descricao="Validade passada",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua C",
        numero="30",
        complemento="",
        estimativa_peso="4.00",
        expira_em="2020-01-01",
    )
    # doação sem expira_em não deve aparecer no resultado
    Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Sem Validade {seed}",
        descricao="Sem data de validade",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua D",
        numero="40",
        complemento="",
        estimativa_peso="5.00",
        expira_em=None,
    )

    response = api_client.get("/doacao/?validade_min=2027-01-01", format="json")

    assert response.status_code == 200
    ids = {item["id"] for item in response.data["data"]}
    assert ids == {doacao_valida.id, doacao_proxima.id}


@pytest.mark.django_db
def test_listagem_de_doacoes_rejeita_data_invalida(api_client):
    response = api_client.get("/doacao/?validade_min=nao-e-uma-data", format="json")

    assert response.status_code == 400
    assert "msg" in response.data


@pytest.mark.django_db
def test_listagem_de_cidades_disponiveis(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"D1 {seed}",
        descricao="",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua A",
        numero="1",
        complemento="",
        estimativa_peso="1.00",
    )
    Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"D2 {seed}",
        descricao="",
        status="disponivel",
        cep="01000000",
        cidade="São Paulo",
        estado="SP",
        bairro="Centro",
        logradouro="Rua B",
        numero="2",
        complemento="",
        estimativa_peso="2.00",
    )
    Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"D3 {seed}",
        descricao="",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Barão",
        logradouro="Rua C",
        numero="3",
        complemento="",
        estimativa_peso="3.00",
    )

    response = api_client.get("/doacao/cidades/", format="json")

    assert response.status_code == 200
    assert "Campinas" in response.data["data"]
    assert "São Paulo" in response.data["data"]
    assert response.data["data"] == sorted(set(response.data["data"]))


@pytest.mark.django_db
def test_listagem_de_doacoes_pode_filtrar_por_uma_cidade(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    doacao_campinas = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Campinas {seed}",
        descricao="",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua A",
        numero="1",
        complemento="",
        estimativa_peso="1.00",
    )
    Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao SP {seed}",
        descricao="",
        status="disponivel",
        cep="01000000",
        cidade="São Paulo",
        estado="SP",
        bairro="Centro",
        logradouro="Rua B",
        numero="2",
        complemento="",
        estimativa_peso="2.00",
    )

    response = api_client.get("/doacao/?cidades=Campinas", format="json")

    assert response.status_code == 200
    ids = {item["id"] for item in response.data["data"]}
    assert ids == {doacao_campinas.id}


@pytest.mark.django_db
def test_listagem_de_doacoes_pode_filtrar_por_multiplas_cidades(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    doacao_campinas = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao Campinas {seed}",
        descricao="",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua A",
        numero="1",
        complemento="",
        estimativa_peso="1.00",
    )
    doacao_sp = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao SP {seed}",
        descricao="",
        status="disponivel",
        cep="01000000",
        cidade="São Paulo",
        estado="SP",
        bairro="Centro",
        logradouro="Rua B",
        numero="2",
        complemento="",
        estimativa_peso="2.00",
    )
    Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doacao RJ {seed}",
        descricao="",
        status="disponivel",
        cep="20000000",
        cidade="Rio de Janeiro",
        estado="RJ",
        bairro="Centro",
        logradouro="Rua C",
        numero="3",
        complemento="",
        estimativa_peso="3.00",
    )

    response = api_client.get("/doacao/?cidades=Campinas,São Paulo", format="json")

    assert response.status_code == 200
    ids = {item["id"] for item in response.data["data"]}
    assert ids == {doacao_campinas.id, doacao_sp.id}


@pytest.mark.django_db
def test_listagem_de_doacoes_pode_filtrar_por_titulo(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    doacao_arroz = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doação de Arroz {seed}",
        descricao="",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua A",
        numero="1",
        complemento="",
        estimativa_peso="2.00",
    )
    Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doação de Feijão {seed}",
        descricao="",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua B",
        numero="2",
        complemento="",
        estimativa_peso="2.00",
    )

    response = api_client.get("/doacao/?busca=Arroz", format="json")

    assert response.status_code == 200
    ids = {item["id"] for item in response.data["data"]}
    assert ids == {doacao_arroz.id}


@pytest.mark.django_db
def test_filtro_por_titulo_e_case_insensitive(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")

    doacao_arroz = Doacao.objects.create(
        doador=doador,
        receptor=None,
        titulo=f"Doação de Arroz {seed}",
        descricao="",
        status="disponivel",
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua A",
        numero="1",
        complemento="",
        estimativa_peso="2.00",
    )

    response = api_client.get("/doacao/?busca=arroz", format="json")

    assert response.status_code == 200
    ids = {item["id"] for item in response.data["data"]}
    assert ids == {doacao_arroz.id}
