import datetime

from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core.models import (
    Alimento,
    Avaliacao,
    Categoria,
    Doacao,
    DoacaoStatus,
    Notificacao,
    SolicitacaoDoacao,
    Usuario,
)
from core.serializers import (
    AlimentoSerializer,
    AuthLoginSerializer,
    AvaliacaoSerializer,
    CategoriaSerializer,
    DoacaoSerializer,
    NotificacaoSerializer,
    SolicitacaoDoacaoSerializer,
    UsuarioSerializer,
)
from core.services import recompute_doacao_derivados

DELETE_ID_SERIALIZER = inline_serializer(
    name="DeleteByIdRequest",
    fields={
        "id": serializers.IntegerField(),
    },
)


def _usuario_response_data(usuario):
    return UsuarioSerializer(usuario).data


def _password_matches(usuario, raw_password):
    try:
        identify_hasher(usuario.password)
    except ValueError:
        if usuario.password == raw_password:
            usuario.password = make_password(raw_password)
            usuario.save(update_fields=["password", "updated_at"])
            return True
        return False
    return check_password(raw_password, usuario.password)


CRUD_EXAMPLES = {
    "usuario": {
        "create": {
            "nome": "Joao Silva",
            "email": "joao@example.com",
            "password": "senha123",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua das Flores",
            "numero": "123",
            "complemento": "Apto 12",
            "foto_perfil_url": "https://example.com/foto.jpg",
        },
        "update": {
            "id": 1,
            "nome": "Joao Silva",
            "email": "joao@example.com",
            "password": "senha123",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua das Flores",
            "numero": "123",
            "complemento": "Apto 12",
            "foto_perfil_url": "https://example.com/foto.jpg",
        },
        "patch": {"id": 1, "bairro": "Taquaral"},
        "item": {
            "id": 1,
            "nome": "Joao Silva",
            "email": "joao@example.com",
            "password": "senha123",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua das Flores",
            "numero": "123",
            "complemento": "Apto 12",
            "foto_perfil_url": "https://example.com/foto.jpg",
            "created_at": "2026-03-24T10:00:00Z",
            "updated_at": "2026-03-24T10:00:00Z",
        },
    },
    "categoria": {
        "create": {"nome": "Frutas"},
        "update": {"id": 1, "nome": "Hortifruti"},
        "patch": {"id": 1, "nome": "Legumes"},
        "item": {"id": 1, "nome": "Frutas"},
    },
    "doacao": {
        "create": {
            "doador": 1,
            "receptor": None,
            "titulo": "Cesta Basica",
            "descricao": "Cesta com alimentos nao pereciveis",
            "status": "disponivel",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua das Flores",
            "numero": "123",
            "complemento": "Casa",
            "estimativa_peso": "12.50",
        },
        "update": {
            "id": 1,
            "doador": 1,
            "receptor": 2,
            "titulo": "Cesta Basica Atualizada",
            "descricao": "Cesta com alimentos nao pereciveis",
            "status": "reservada",
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua das Flores",
            "numero": "123",
            "complemento": "Casa",
            "estimativa_peso": "12.50",
        },
        "patch": {"id": 1, "status": "concluida", "confirmacao_usuario_id": 1},
        "item": {
            "id": 1,
            "doador": 1,
            "receptor": 2,
            "titulo": "Cesta Basica",
            "descricao": "Cesta com alimentos nao pereciveis",
            "status": "disponivel",
            "data_publicacao": "2026-03-24T10:00:00Z",
            "data_reserva": None,
            "data_conclusao": None,
            "cep": "13000000",
            "cidade": "Campinas",
            "estado": "SP",
            "bairro": "Centro",
            "logradouro": "Rua das Flores",
            "numero": "123",
            "complemento": "Casa",
            "expira_em": None,
            "estimativa_peso": "12.50",
            "created_at": "2026-03-24T10:00:00Z",
            "updated_at": "2026-03-24T10:00:00Z",
        },
    },
    "solicitacao-doacao": {
        "create": {
            "doacao": 1,
            "solicitante": 2,
            "status": "pendente",
            "mensagem": "Tenho interesse.",
        },
        "update": {
            "id": 1,
            "doacao": 1,
            "solicitante": 2,
            "status": "aceita",
            "mensagem": "Tenho interesse.",
        },
        "patch": {"id": 1, "status": "recusada"},
        "item": {
            "id": 1,
            "doacao": 1,
            "solicitante": 2,
            "status": "pendente",
            "mensagem": "Tenho interesse.",
            "data_solicitacao": "2026-03-24T10:00:00Z",
            "data_resposta": None,
        },
    },
    "alimento": {
        "create": {
            "categoria": 1,
            "doacao": 1,
            "nome": "Arroz",
            "data_validade": "2026-12-31",
            "quantidade": "5.00",
            "unidade": "kg",
        },
        "update": {
            "id": 1,
            "categoria": 1,
            "doacao": 1,
            "nome": "Arroz Integral",
            "data_validade": "2026-12-31",
            "quantidade": "5.00",
            "unidade": "kg",
        },
        "patch": {"id": 1, "quantidade": "3.00"},
        "item": {
            "id": 1,
            "categoria": 1,
            "doacao": 1,
            "nome": "Arroz",
            "data_validade": "2026-12-31",
            "quantidade": "5.00",
            "unidade": "kg",
        },
    },
    "notificacao": {
        "create": {
            "usuario": 1,
            "doacao": 1,
            "mensagem": "Nova solicitacao recebida.",
            "status": "pendente",
        },
        "update": {
            "id": 1,
            "usuario": 1,
            "doacao": 1,
            "mensagem": "Nova solicitacao recebida.",
            "status": "lida",
        },
        "patch": {"id": 1, "status": "lida"},
        "item": {
            "id": 1,
            "usuario": 1,
            "doacao": 1,
            "mensagem": "Nova solicitacao recebida.",
            "status": "pendente",
            "lida_em": None,
            "created_at": "2026-03-24T10:00:00Z",
        },
    },
    "avaliacao": {
        "create": {
            "doacao": 1,
            "avaliador": 2,
            "avaliado": 1,
            "nota": 5,
            "comentario": "Excelente atendimento.",
        },
        "update": {
            "id": 1,
            "doacao": 1,
            "avaliador": 2,
            "avaliado": 1,
            "nota": 4,
            "comentario": "Muito bom.",
        },
        "patch": {"id": 1, "nota": 5},
        "item": {
            "id": 1,
            "doacao": 1,
            "avaliador": 2,
            "avaliado": 1,
            "nota": 5,
            "comentario": "Excelente atendimento.",
            "created_at": "2026-03-24T10:00:00Z",
        },
    },
}


def _success_response_serializer(serializer_class, name, many=False):
    data_field = serializer_class(many=True) if many else serializer_class()
    return inline_serializer(
        name=name,
        fields={
            "msg": serializers.CharField(),
            "data": data_field,
        },
    )


# serve para enriquecer a documentação que aparece no swagger
def crud_docs(serializer_class, tag):
    # Add explicit method schemas so Swagger can render request bodies.
    examples = CRUD_EXAMPLES.get(tag, {})
    resource_name = tag.replace("-", " ").title()
    item_response = _success_response_serializer(
        serializer_class, f"{resource_name}SuccessResponse"
    )
    list_response = _success_response_serializer(
        serializer_class, f"{resource_name}ListSuccessResponse", many=True
    )

    def decorator(func):
        func = extend_schema(
            methods=["GET"],
            tags=[tag],
            summary=f"Listar {resource_name}",
            description=f"Retorna todos os registros de {resource_name}.",
            responses={
                200: OpenApiResponse(
                    response=list_response,
                    description="Lista retornada com sucesso.",
                    examples=[
                        OpenApiExample(
                            f"{resource_name} GET Response",
                            value={
                                "msg": "Successfully retrieved data",
                                "data": [examples.get("item", {"id": 1})],
                            },
                            response_only=True,
                        ),
                    ],
                ),
            },
        )(func)
        func = extend_schema(
            methods=["POST"],
            tags=[tag],
            summary=f"Criar {resource_name}",
            description=f"Cria um novo registro de {resource_name}.",
            request=serializer_class,
            examples=[
                OpenApiExample(
                    f"{resource_name} POST Request",
                    value=examples.get("create", {}),
                    request_only=True,
                ),
            ],
            responses={
                201: OpenApiResponse(
                    response=item_response,
                    description="Registro criado com sucesso.",
                    examples=[
                        OpenApiExample(
                            f"{resource_name} POST Response",
                            value={
                                "msg": f"{resource_name} created successfully",
                                "data": examples.get("item", {"id": 1}),
                            },
                            response_only=True,
                        ),
                    ],
                ),
            },
        )(func)
        func = extend_schema(
            methods=["PUT"],
            tags=[tag],
            summary=f"Atualizar {resource_name} completo",
            description="Atualiza todos os campos do registro. Requer o campo id no body.",
            request=serializer_class,
            examples=[
                OpenApiExample(
                    f"{resource_name} PUT Request",
                    value=examples.get("update", {"id": 1}),
                    request_only=True,
                ),
            ],
            responses={
                200: OpenApiResponse(
                    response=item_response,
                    description="Registro atualizado com sucesso.",
                ),
            },
        )(func)
        func = extend_schema(
            methods=["PATCH"],
            tags=[tag],
            summary=f"Atualizar {resource_name} parcial",
            description="Atualiza parcialmente o registro. Requer o campo id no body.",
            request=serializer_class,
            examples=[
                OpenApiExample(
                    f"{resource_name} PATCH Request",
                    value=examples.get("patch", {"id": 1}),
                    request_only=True,
                ),
            ],
            responses={
                200: OpenApiResponse(
                    response=item_response,
                    description="Registro atualizado parcialmente com sucesso.",
                ),
            },
        )(func)
        return func

    return decorator


# Create your views here.
@api_view()
def view_dtl(request):
    return Response({"success": 409, "message": "api"})


@extend_schema(
    tags=["auth"],
    summary="Cadastrar usuário",
    request=UsuarioSerializer,
    responses={201: UsuarioSerializer},
)
@api_view(["POST"])
def view_auth_register(request):
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        usuario = serializer.save()
        return Response(
            {"msg": "Usuario registered successfully", "data": _usuario_response_data(usuario)},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["auth"],
    summary="Entrar com e-mail e senha",
    request=AuthLoginSerializer,
    responses={200: UsuarioSerializer},
)
@api_view(["POST"])
def view_auth_login(request):
    serializer = AuthLoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"].strip()
    password = serializer.validated_data["password"]

    try:
        usuario = Usuario.objects.get(email__iexact=email)
    except Usuario.DoesNotExist:
        return Response(
            {"msg": "E-mail ou senha invalidos."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not _password_matches(usuario, password):
        return Response(
            {"msg": "E-mail ou senha invalidos."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return Response(
        {"msg": "Login successful", "data": _usuario_response_data(usuario)},
        status=status.HTTP_200_OK,
    )


def _handle_crud(request, model, serializer_class, resource_name):
    """Trata GET/POST/PUT/PATCH genérico para recursos sem filtros customizados."""
    if request.method == "GET":
        serializer = serializer_class(model.objects.all(), many=True)
        return Response(
            {"msg": "Successfully retrieved data", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    elif request.method == "POST":
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": f"{resource_name} created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        obj = model.objects.get(pk=request.data.get("id"))
        serializer = serializer_class(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": f"{resource_name} updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PATCH":
        obj = model.objects.get(pk=request.data.get("id"))
        serializer = serializer_class(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": f"{resource_name} updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"msg": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def _handle_detail(request, model, serializer_class, resource_name, id):
    """Trata GET/DELETE genérico para um recurso individual por ID."""
    try:
        obj = model.objects.get(pk=id)
        if request.method == "GET":
            serializer = serializer_class(obj)
            return Response(
                {"msg": "Successfully retrieved data", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        elif request.method == "DELETE":
            obj.delete()
            return Response(
                {"msg": f"{resource_name} deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
    except model.DoesNotExist:
        return Response({"msg": f"{resource_name} not found"}, status=status.HTTP_404_NOT_FOUND)


# Usuario Views
@crud_docs(UsuarioSerializer, "usuario")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_usuario(request):
    return _handle_crud(request, Usuario, UsuarioSerializer, "Usuario")


# Categoria Views
@crud_docs(CategoriaSerializer, "categoria")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_categoria(request):
    return _handle_crud(request, Categoria, CategoriaSerializer, "Categoria")


# Doacao Views
def _aplicar_filtros_doacao(queryset, query_params):
    """Aplica os filtros recebidos via query params ao queryset de Doacao.

    Retorna o queryset filtrado ou uma Response de erro (400) caso algum
    parâmetro seja inválido.
    """
    categoria_id = query_params.get("categoria")
    if categoria_id:
        queryset = queryset.filter(alimentos__categoria_id=categoria_id).distinct()

    status_filtro = query_params.get("status")
    if status_filtro:
        valores_validos = DoacaoStatus.values
        if status_filtro not in valores_validos:
            return Response(
                {
                    "msg": (
                        f"Status invalido: '{status_filtro}'. "
                        f"Valores aceitos: {', '.join(valores_validos)}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = queryset.filter(status=status_filtro)

    peso_max = query_params.get("peso_max")
    if peso_max:
        queryset = queryset.filter(
            estimativa_peso__isnull=False,
            estimativa_peso__lte=peso_max,
        )

    validade_min = query_params.get("validade_min")
    if validade_min:
        try:
            data_validade_min = datetime.date.fromisoformat(validade_min)
        except ValueError:
            return Response(
                {
                    "msg": (
                        f"Data invalida: '{validade_min}'. "
                        "Use o formato YYYY-MM-DD (ex: 2026-12-31)."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = queryset.filter(
            expira_em__isnull=False,
            expira_em__gte=data_validade_min,
        )

    cidades_param = query_params.get("cidades")
    if cidades_param:
        cidades_lista = [c.strip() for c in cidades_param.split(",") if c.strip()]
        if cidades_lista:
            queryset = queryset.filter(cidade__in=cidades_lista)

    busca = query_params.get("busca")
    if busca:
        queryset = queryset.filter(titulo__icontains=busca)

    return queryset


@crud_docs(DoacaoSerializer, "doacao")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_doacao(request):
    if request.method == "GET":
        queryset = _aplicar_filtros_doacao(Doacao.objects.all(), request.query_params)
        if isinstance(queryset, Response):
            return queryset
        serializer = DoacaoSerializer(queryset, many=True)
        return Response(
            {"msg": "Successfully retrieved data", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    elif request.method == "POST":
        serializer = DoacaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Doacao created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        doacao_obj = Doacao.objects.get(pk=request.data.get("id"))
        serializer = DoacaoSerializer(doacao_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Doacao updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PATCH":
        doacao_obj = Doacao.objects.get(pk=request.data.get("id"))
        serializer = DoacaoSerializer(doacao_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Doacao updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"msg": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["GET"])
def view_doacao_cidades(request):
    """Retorna lista ordenada de cidades distintas que possuem doações cadastradas."""
    cidades = (
        Doacao.objects.exclude(cidade__isnull=True)
        .exclude(cidade="")
        .values_list("cidade", flat=True)
        .distinct()
        .order_by("cidade")
    )
    return Response(
        {"msg": "Successfully retrieved data", "data": list(cidades)},
        status=status.HTTP_200_OK,
    )


# SolicitacaoDoacao Views
@crud_docs(SolicitacaoDoacaoSerializer, "solicitacao-doacao")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_solicitacao_doacao(request):
    return _handle_crud(
        request, SolicitacaoDoacao, SolicitacaoDoacaoSerializer, "SolicitacaoDoacao"
    )


# Alimento Views
@crud_docs(AlimentoSerializer, "alimento")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_alimento(request):
    return _handle_crud(request, Alimento, AlimentoSerializer, "Alimento")


# Notificacao Views
@crud_docs(NotificacaoSerializer, "notificacao")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_notificacao(request):
    return _handle_crud(request, Notificacao, NotificacaoSerializer, "Notificacao")


# Avaliacao Views
@crud_docs(AvaliacaoSerializer, "avaliacao")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_avaliacao(request):
    if request.method == "GET":
        avaliacao_obj = Avaliacao.objects.all()
        for filtro, campo in {
            "doacao": "doacao_id",
            "avaliado": "avaliado_id",
            "avaliador": "avaliador_id",
        }.items():
            valor = request.query_params.get(filtro)
            if not valor:
                continue
            try:
                valor = int(valor)
            except ValueError:
                return Response(
                    {
                        "msg": (
                            f"Filtro invalido para {filtro}: '{valor}'. " "Informe um id numerico."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            avaliacao_obj = avaliacao_obj.filter(**{campo: valor})

        serializer = AvaliacaoSerializer(avaliacao_obj, many=True)
        return Response(
            {"msg": "Successfully retrieved data", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    elif request.method == "POST":
        serializer = AvaliacaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Avaliacao created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        avaliacao_obj = Avaliacao.objects.get(pk=request.data.get("id"))
        serializer = AvaliacaoSerializer(avaliacao_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Avaliacao updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PATCH":
        avaliacao_obj = Avaliacao.objects.get(pk=request.data.get("id"))
        serializer = AvaliacaoSerializer(avaliacao_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Avaliacao updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"msg": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Detail Views (GET/DELETE individual by ID)
def detail_docs(serializer_class, tag):
    examples = CRUD_EXAMPLES.get(tag, {})
    resource_name = tag.replace("-", " ").title()
    item_response = _success_response_serializer(
        serializer_class, f"{resource_name}DetailSuccessResponse"
    )

    def decorator(func):
        func = extend_schema(
            methods=["GET"],
            tags=[tag],
            summary=f"Obter {resource_name} por ID",
            description=f"Retorna um registro específico de {resource_name}.",
            responses={
                200: OpenApiResponse(
                    response=item_response,
                    description="Registro obtido com sucesso.",
                    examples=[
                        OpenApiExample(
                            f"{resource_name} GET Detail Response",
                            value={
                                "msg": "Successfully retrieved data",
                                "data": examples.get("item", {"id": 1}),
                            },
                            response_only=True,
                        ),
                    ],
                ),
            },
        )(func)
        func = extend_schema(
            methods=["DELETE"],
            tags=[tag],
            summary=f"Deletar {resource_name}",
            description=f"Remove um registro específico de {resource_name}.",
            responses={
                204: OpenApiResponse(description="Registro removido com sucesso."),
            },
        )(func)
        return func

    return decorator


@detail_docs(UsuarioSerializer, "usuario")
@api_view(["GET", "DELETE"])
def view_usuario_detail(request, id):
    return _handle_detail(request, Usuario, UsuarioSerializer, "Usuario", id)


@detail_docs(CategoriaSerializer, "categoria")
@api_view(["GET", "DELETE"])
def view_categoria_detail(request, id):
    return _handle_detail(request, Categoria, CategoriaSerializer, "Categoria", id)


@detail_docs(DoacaoSerializer, "doacao")
@api_view(["GET", "DELETE"])
def view_doacao_detail(request, id):
    return _handle_detail(request, Doacao, DoacaoSerializer, "Doacao", id)


@detail_docs(SolicitacaoDoacaoSerializer, "solicitacao-doacao")
@api_view(["GET", "DELETE"])
def view_solicitacao_doacao_detail(request, id):
    return _handle_detail(
        request, SolicitacaoDoacao, SolicitacaoDoacaoSerializer, "SolicitacaoDoacao", id
    )


@detail_docs(AlimentoSerializer, "alimento")
@api_view(["GET", "DELETE"])
def view_alimento_detail(request, id):
    try:
        alimento_obj = Alimento.objects.get(pk=id)
        if request.method == "GET":
            serializer = AlimentoSerializer(alimento_obj)
            return Response(
                {"msg": "Successfully retrieved data", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        elif request.method == "DELETE":
            doacao = alimento_obj.doacao
            alimento_obj.delete()
            recompute_doacao_derivados(doacao)
            return Response(
                {"msg": "Alimento deleted successfully"}, status=status.HTTP_204_NO_CONTENT
            )
    except Alimento.DoesNotExist:
        return Response({"msg": "Alimento not found"}, status=status.HTTP_404_NOT_FOUND)


@detail_docs(NotificacaoSerializer, "notificacao")
@api_view(["GET", "DELETE"])
def view_notificacao_detail(request, id):
    return _handle_detail(request, Notificacao, NotificacaoSerializer, "Notificacao", id)


@detail_docs(AvaliacaoSerializer, "avaliacao")
@api_view(["GET", "DELETE"])
def view_avaliacao_detail(request, id):
    return _handle_detail(request, Avaliacao, AvaliacaoSerializer, "Avaliacao", id)
