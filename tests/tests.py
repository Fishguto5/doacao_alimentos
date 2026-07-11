import uuid

import pytest
from django.contrib.auth.hashers import check_password
from django.utils import timezone
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
        doacao_concluida = resource == "avaliacao"
        dependencies["categoria"] = Categoria.objects.create(nome=f"Categoria {seed}")
        dependencies["doacao"] = Doacao.objects.create(
            doador=dependencies["doador"],
            receptor=dependencies["receptor"],
            titulo=f"Doacao Base {seed}",
            descricao="Doacao criada para testes",
            status="concluida" if doacao_concluida else "disponivel",
            data_conclusao=timezone.now() if doacao_concluida else None,
            concluida_por_doador=doacao_concluida,
            concluida_por_receptor=doacao_concluida,
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
            "avaliador": dependencies["receptor"].id,
            "avaliado": dependencies["doador"].id,
            "nota": 4,
            "comentario": f"Avaliacao inicial {seed}",
        }
        put_payload = {
            "doacao": dependencies["doacao"].id,
            "avaliador": dependencies["receptor"].id,
            "avaliado": dependencies["doador"].id,
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


def _create_doacao_para_avaliacao(
    seed: str,
    status_doacao: str = "concluida",
    doador: Usuario | None = None,
    receptor: Usuario | None = None,
) -> tuple[Doacao, Usuario, Usuario]:
    doador = doador or _create_usuario(f"{seed}_doador", "DoadorAval")
    receptor = receptor or _create_usuario(f"{seed}_receptor", "ReceptorAval")
    concluida = status_doacao == "concluida"
    doacao = Doacao.objects.create(
        doador=doador,
        receptor=receptor,
        titulo=f"Doacao Avaliacao {seed}",
        descricao="Doacao criada para testar avaliacoes",
        status=status_doacao,
        data_conclusao=timezone.now() if concluida else None,
        concluida_por_doador=concluida,
        concluida_por_receptor=concluida,
        cep="13000000",
        cidade="Campinas",
        estado="SP",
        bairro="Centro",
        logradouro="Rua Avaliacao",
        numero="100",
        complemento="",
        estimativa_peso="8.00",
    )
    return doacao, doador, receptor


def _usuario_payload(seed: str, prefix: str = "Usuario") -> dict:
    return {
        "nome": f"{prefix} {seed}",
        "email": f"{prefix.lower()}_{seed}@example.com",
        "password": "senha12345",
        "cep": "13000000",
        "cidade": "Campinas",
        "estado": "SP",
        "bairro": "Centro",
        "logradouro": "Rua Auth",
        "numero": "10",
        "complemento": "",
        "foto_perfil_url": "",
    }


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
def test_auth_register_cria_usuario_com_senha_hash_e_nao_retorna_password(api_client):
    seed = uuid.uuid4().hex[:8]
    payload = _usuario_payload(seed, "Auth")

    response = api_client.post("/auth/register/", data=payload, format="json")

    assert response.status_code == 201
    assert "password" not in response.data["data"]
    usuario = Usuario.objects.get(pk=response.data["data"]["id"])
    assert usuario.password != payload["password"]
    assert check_password(payload["password"], usuario.password)


@pytest.mark.django_db
def test_auth_login_valida_email_e_senha(api_client):
    seed = uuid.uuid4().hex[:8]
    payload = _usuario_payload(seed, "Login")
    register_response = api_client.post("/auth/register/", data=payload, format="json")
    assert register_response.status_code == 201

    login_response = api_client.post(
        "/auth/login/",
        data={"email": payload["email"].upper(), "password": payload["password"]},
        format="json",
    )

    assert login_response.status_code == 200
    assert login_response.data["data"]["email"] == payload["email"]
    assert "password" not in login_response.data["data"]


@pytest.mark.django_db
def test_auth_login_rejeita_senha_incorreta(api_client):
    seed = uuid.uuid4().hex[:8]
    payload = _usuario_payload(seed, "LoginFail")
    register_response = api_client.post("/auth/register/", data=payload, format="json")
    assert register_response.status_code == 201

    login_response = api_client.post(
        "/auth/login/",
        data={"email": payload["email"], "password": "senha_errada"},
        format="json",
    )

    assert login_response.status_code == 401
    assert "msg" in login_response.data


@pytest.mark.django_db
def test_receptor_pode_avaliar_doacao_concluida(api_client):
    seed = uuid.uuid4().hex[:8]
    doacao, doador, receptor = _create_doacao_para_avaliacao(seed)

    response = api_client.post(
        "/avaliacao/",
        data={
            "doacao": doacao.id,
            "avaliador": receptor.id,
            "avaliado": doador.id,
            "nota": 5,
            "comentario": "Doacao recebida conforme combinado.",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.data["data"]["doacao"] == doacao.id
    assert response.data["data"]["avaliador"] == receptor.id
    assert response.data["data"]["avaliado"] == doador.id


@pytest.mark.django_db
def test_doador_nao_pode_avaliar_doacao_mesmo_concluida(api_client):
    seed = uuid.uuid4().hex[:8]
    doacao, doador, receptor = _create_doacao_para_avaliacao(seed)

    response = api_client.post(
        "/avaliacao/",
        data={
            "doacao": doacao.id,
            "avaliador": doador.id,
            "avaliado": receptor.id,
            "nota": 4,
            "comentario": "Tentativa invalida do doador.",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "avaliador" in response.data
    assert not Avaliacao.objects.filter(doacao=doacao, avaliador=doador).exists()


@pytest.mark.django_db
def test_receptor_nao_pode_avaliar_doacao_nao_concluida(api_client):
    seed = uuid.uuid4().hex[:8]
    doacao, doador, receptor = _create_doacao_para_avaliacao(
        seed,
        status_doacao="reservada",
    )

    response = api_client.post(
        "/avaliacao/",
        data={
            "doacao": doacao.id,
            "avaliador": receptor.id,
            "avaliado": doador.id,
            "nota": 5,
            "comentario": "Tentativa antes da conclusao.",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "doacao" in response.data
    assert not Avaliacao.objects.filter(doacao=doacao).exists()


@pytest.mark.django_db
def test_qualquer_usuario_pode_listar_avaliacoes_de_uma_doacao(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(f"{seed}_doador", "DoadorAval")
    receptor = _create_usuario(f"{seed}_receptor", "ReceptorAval")
    doacao_um, _, _ = _create_doacao_para_avaliacao(
        f"{seed}_um",
        doador=doador,
        receptor=receptor,
    )
    doacao_dois, _, _ = _create_doacao_para_avaliacao(
        f"{seed}_dois",
        doador=doador,
        receptor=receptor,
    )
    avaliacao_um = Avaliacao.objects.create(
        doacao=doacao_um,
        avaliador=receptor,
        avaliado=doador,
        nota=5,
        comentario="Avaliacao da primeira doacao.",
    )
    avaliacao_dois = Avaliacao.objects.create(
        doacao=doacao_dois,
        avaliador=receptor,
        avaliado=doador,
        nota=3,
        comentario="Avaliacao de outra doacao.",
    )

    response = api_client.get(f"/avaliacao/?doacao={doacao_um.id}", format="json")

    assert response.status_code == 200
    assert [avaliacao["id"] for avaliacao in response.data["data"]] == [
        avaliacao_um.id,
    ]

    response_avaliado = api_client.get(f"/avaliacao/?avaliado={doador.id}", format="json")

    assert response_avaliado.status_code == 200
    ids_avaliado = {avaliacao["id"] for avaliacao in response_avaliado.data["data"]}
    assert ids_avaliado == {avaliacao_um.id, avaliacao_dois.id}


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
def test_estimativa_peso_da_doacao_e_calculada_pelos_alimentos(api_client):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    categoria = Categoria.objects.create(nome=f"Categoria Peso {seed}")

    resp_doacao = api_client.post(
        "/doacao/",
        data={
            "doador": doador.id,
            "receptor": None,
            "titulo": f"Doacao Peso {seed}",
            "descricao": "Teste de peso automatico",
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua Peso",
            "numero": "10",
            "complemento": "",
            "estimativa_peso": "99.00",
        },
        format="json",
    )
    assert resp_doacao.status_code == 201
    doacao_id = resp_doacao.data["data"]["id"]

    alimentos = [
        ("Arroz", "2.00", "kg"),
        ("Feijao", "500.00", "g"),
        ("Leite", "1.00", "l"),
        ("Molho", "250.00", "ml"),
        ("Pao", "10.00", "unidade"),
    ]
    alimento_ids = {}
    for nome, quantidade, unidade in alimentos:
        resp_alimento = api_client.post(
            "/alimento/",
            data={
                "categoria": categoria.id,
                "doacao": doacao_id,
                "nome": f"{nome} {seed}",
                "data_validade": "2026-12-31",
                "quantidade": quantidade,
                "unidade": unidade,
            },
            format="json",
        )
        assert resp_alimento.status_code == 201
        alimento_ids[nome] = resp_alimento.data["data"]["id"]

    detail = api_client.get(f"/doacao/{doacao_id}/", format="json")

    assert detail.status_code == 200
    assert detail.data["data"]["estimativa_peso"] == "3.75"

    resp_update = api_client.patch(
        "/alimento/",
        data={"id": alimento_ids["Feijao"], "quantidade": "900.00"},
        format="json",
    )
    assert resp_update.status_code == 200

    detail_atualizado = api_client.get(f"/doacao/{doacao_id}/", format="json")
    assert detail_atualizado.data["data"]["estimativa_peso"] == "4.15"

    resp_delete = api_client.delete(f"/alimento/{alimento_ids['Leite']}/", format="json")
    assert resp_delete.status_code == 204

    detail_apos_delete = api_client.get(f"/doacao/{doacao_id}/", format="json")
    assert detail_apos_delete.data["data"]["estimativa_peso"] == "3.15"


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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "unidade, quantidade, expected_status",
    [
        # unidade - valid (1, 100, 1.00)
        ("unidade", "1.00", 201),
        ("unidade", "50.00", 201),
        ("unidade", "100.00", 201),
        # unidade - invalid (0, -1, 1.5, 101)
        ("unidade", "0.00", 400),
        ("unidade", "-5.00", 400),
        ("unidade", "1.50", 400),
        ("unidade", "101.00", 400),

        # kg - valid (0.01, 50.00, 100.00)
        ("kg", "0.01", 201),
        ("kg", "50.50", 201),
        ("kg", "100.00", 201),
        # kg - invalid (0.00, -1.00, 100.01)
        ("kg", "0.00", 400),
        ("kg", "-1.00", 400),
        ("kg", "100.01", 400),

        # g - valid (50.00, 500.00, 999.00)
        ("g", "50.00", 201),
        ("g", "500.00", 201),
        ("g", "999.00", 201),
        # g - invalid (49.00, 250.50, 1000.00, -10.00)
        ("g", "49.00", 400),
        ("g", "250.50", 400),
        ("g", "1000.00", 400),
        ("g", "-10.00", 400),

        # l - valid (0.01, 1.50, 100.00)
        ("l", "0.01", 201),
        ("l", "1.50", 201),
        ("l", "100.00", 201),
        # l - invalid (0.00, -2.00, 100.01)
        ("l", "0.00", 400),
        ("l", "-2.00", 400),
        ("l", "100.01", 400),

        # ml - valid (50.00, 350.00, 999.00)
        ("ml", "50.00", 201),
        ("ml", "350.00", 201),
        ("ml", "999.00", 201),
        # ml - invalid (49.00, 350.50, 1000.00, -5.00)
        ("ml", "49.00", 400),
        ("ml", "350.50", 400),
        ("ml", "1000.00", 400),
        ("ml", "-5.00", 400),
    ],
)
def test_validacao_quantidade_por_unidade_medida(api_client, unidade, quantidade, expected_status):
    seed = uuid.uuid4().hex[:8]
    doador = _create_usuario(seed, "Doador")
    categoria = Categoria.objects.create(nome=f"Categoria Teste {seed}")
    doacao = Doacao.objects.create(
        doador=doador,
        titulo=f"Doacao Teste {seed}",
        status="disponivel",
        cidade="Campinas",
        estado="SP",
    )

    response = api_client.post(
        "/alimento/",
        data={
            "categoria": categoria.id,
            "doacao": doacao.id,
            "nome": f"Alimento Teste {seed}",
            "data_validade": "2026-12-31",
            "quantidade": quantidade,
            "unidade": unidade,
        },
        format="json",
    )

    assert response.status_code == expected_status
    if expected_status == 400:
        assert "quantidade" in response.data
