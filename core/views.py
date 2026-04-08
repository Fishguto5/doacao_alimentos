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
    Notificacao,
    Person,
    SolicitacaoDoacao,
    Usuario,
)
from core.serializers import (
    AlimentoSerializer,
    AvaliacaoSerializer,
    CategoriaSerializer,
    DoacaoSerializer,
    NotificacaoSerializer,
    PersonSerializer,
    SolicitacaoDoacaoSerializer,
    UsuarioSerializer,
)
from core.services import recompute_doacao_expiracao

DELETE_ID_SERIALIZER = inline_serializer(
    name="DeleteByIdRequest",
    fields={
        "id": serializers.IntegerField(),
    },
)


CRUD_EXAMPLES = {
    "person": {
        "create": {"name": "Maria", "age": 23, "city": "Campinas"},
        "update": {"id": 1, "name": "Maria Souza", "age": 24, "city": "Campinas"},
        "patch": {"id": 1, "city": "Valinhos"},
        "item": {"id": 1, "name": "Maria Souza", "age": 24, "city": "Campinas"},
    },
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
        "patch": {"id": 1, "status": "concluida"},
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


# Métodos análogos são implementadas para cada modelo.
@crud_docs(PersonSerializer, "person")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_person(request):
    # GET method to retrieve all persons
    if request.method == "GET":
        person_obj = Person.objects.all()
        serializer = PersonSerializer(person_obj, many=True)
        return Response(
            {"msg": "Successfully retrieved data", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    # POST method to create a new person
    elif request.method == "POST":
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Person created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT method to update a person (full update)
    elif request.method == "PUT":
        person_obj = Person.objects.get(pk=request.data.get("id"))
        serializer = PersonSerializer(person_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Person updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH method to partially update a person
    elif request.method == "PATCH":
        person_obj = Person.objects.get(pk=request.data.get("id"))
        serializer = PersonSerializer(person_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Person updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"msg": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Usuario Views
@crud_docs(UsuarioSerializer, "usuario")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_usuario(request):
    if request.method == "GET":
        usuario_obj = Usuario.objects.all()
        serializer = UsuarioSerializer(usuario_obj, many=True)
        return Response(
            {"msg": "Successfully retrieved data", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    elif request.method == "POST":
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Usuario created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        usuario_obj = Usuario.objects.get(pk=request.data.get("id"))
        serializer = UsuarioSerializer(usuario_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Usuario updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PATCH":
        usuario_obj = Usuario.objects.get(pk=request.data.get("id"))
        serializer = UsuarioSerializer(usuario_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Usuario updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"msg": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Categoria Views
@crud_docs(CategoriaSerializer, "categoria")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_categoria(request):
    if request.method == "GET":
        categoria_obj = Categoria.objects.all()
        serializer = CategoriaSerializer(categoria_obj, many=True)
        return Response(
            {"msg": "Successfully retrieved data", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    elif request.method == "POST":
        serializer = CategoriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Categoria created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        categoria_obj = Categoria.objects.get(pk=request.data.get("id"))
        serializer = CategoriaSerializer(categoria_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Categoria updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PATCH":
        categoria_obj = Categoria.objects.get(pk=request.data.get("id"))
        serializer = CategoriaSerializer(categoria_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Categoria updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"msg": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Doacao Views
@crud_docs(DoacaoSerializer, "doacao")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_doacao(request):
    if request.method == "GET":
        doacao_obj = Doacao.objects.all()
        serializer = DoacaoSerializer(doacao_obj, many=True)
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


# SolicitacaoDoacao Views
@crud_docs(SolicitacaoDoacaoSerializer, "solicitacao-doacao")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_solicitacao_doacao(request):
    if request.method == "GET":
        solicitacao_obj = SolicitacaoDoacao.objects.all()
        serializer = SolicitacaoDoacaoSerializer(solicitacao_obj, many=True)
        return Response(
            {"msg": "Successfully retrieved data", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    elif request.method == "POST":
        serializer = SolicitacaoDoacaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "SolicitacaoDoacao created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        solicitacao_obj = SolicitacaoDoacao.objects.get(pk=request.data.get("id"))
        serializer = SolicitacaoDoacaoSerializer(solicitacao_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "SolicitacaoDoacao updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PATCH":
        solicitacao_obj = SolicitacaoDoacao.objects.get(pk=request.data.get("id"))
        serializer = SolicitacaoDoacaoSerializer(solicitacao_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "SolicitacaoDoacao updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"msg": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Alimento Views
@crud_docs(AlimentoSerializer, "alimento")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_alimento(request):
    if request.method == "GET":
        alimento_obj = Alimento.objects.all()
        serializer = AlimentoSerializer(alimento_obj, many=True)
        return Response(
            {"msg": "Successfully retrieved data", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    elif request.method == "POST":
        serializer = AlimentoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Alimento created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        alimento_obj = Alimento.objects.get(pk=request.data.get("id"))
        serializer = AlimentoSerializer(alimento_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Alimento updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PATCH":
        alimento_obj = Alimento.objects.get(pk=request.data.get("id"))
        serializer = AlimentoSerializer(alimento_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Alimento updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"msg": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Notificacao Views
@crud_docs(NotificacaoSerializer, "notificacao")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_notificacao(request):
    if request.method == "GET":
        notificacao_obj = Notificacao.objects.all()
        serializer = NotificacaoSerializer(notificacao_obj, many=True)
        return Response(
            {"msg": "Successfully retrieved data", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    elif request.method == "POST":
        serializer = NotificacaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Notificacao created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PUT":
        notificacao_obj = Notificacao.objects.get(pk=request.data.get("id"))
        serializer = NotificacaoSerializer(notificacao_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Notificacao updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PATCH":
        notificacao_obj = Notificacao.objects.get(pk=request.data.get("id"))
        serializer = NotificacaoSerializer(notificacao_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Notificacao updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"msg": "Invalid request method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Avaliacao Views
@crud_docs(AvaliacaoSerializer, "avaliacao")
@api_view(["GET", "POST", "PUT", "PATCH"])
def view_avaliacao(request):
    if request.method == "GET":
        avaliacao_obj = Avaliacao.objects.all()
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


@detail_docs(PersonSerializer, "person")
@api_view(["GET", "DELETE"])
def view_person_detail(request, id):
    try:
        person_obj = Person.objects.get(pk=id)
        if request.method == "GET":
            serializer = PersonSerializer(person_obj)
            return Response(
                {"msg": "Successfully retrieved data", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        elif request.method == "DELETE":
            person_obj.delete()
            return Response(
                {"msg": "Person deleted successfully"}, status=status.HTTP_204_NO_CONTENT
            )
    except Person.DoesNotExist:
        return Response({"msg": "Person not found"}, status=status.HTTP_404_NOT_FOUND)


@detail_docs(UsuarioSerializer, "usuario")
@api_view(["GET", "DELETE"])
def view_usuario_detail(request, id):
    try:
        usuario_obj = Usuario.objects.get(pk=id)
        if request.method == "GET":
            serializer = UsuarioSerializer(usuario_obj)
            return Response(
                {"msg": "Successfully retrieved data", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        elif request.method == "DELETE":
            usuario_obj.delete()
            return Response(
                {"msg": "Usuario deleted successfully"}, status=status.HTTP_204_NO_CONTENT
            )
    except Usuario.DoesNotExist:
        return Response({"msg": "Usuario not found"}, status=status.HTTP_404_NOT_FOUND)


@detail_docs(CategoriaSerializer, "categoria")
@api_view(["GET", "DELETE"])
def view_categoria_detail(request, id):
    try:
        categoria_obj = Categoria.objects.get(pk=id)
        if request.method == "GET":
            serializer = CategoriaSerializer(categoria_obj)
            return Response(
                {"msg": "Successfully retrieved data", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        elif request.method == "DELETE":
            categoria_obj.delete()
            return Response(
                {"msg": "Categoria deleted successfully"}, status=status.HTTP_204_NO_CONTENT
            )
    except Categoria.DoesNotExist:
        return Response({"msg": "Categoria not found"}, status=status.HTTP_404_NOT_FOUND)


@detail_docs(DoacaoSerializer, "doacao")
@api_view(["GET", "DELETE"])
def view_doacao_detail(request, id):
    try:
        doacao_obj = Doacao.objects.get(pk=id)
        if request.method == "GET":
            serializer = DoacaoSerializer(doacao_obj)
            return Response(
                {"msg": "Successfully retrieved data", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        elif request.method == "DELETE":
            doacao_obj.delete()
            return Response(
                {"msg": "Doacao deleted successfully"}, status=status.HTTP_204_NO_CONTENT
            )
    except Doacao.DoesNotExist:
        return Response({"msg": "Doacao not found"}, status=status.HTTP_404_NOT_FOUND)


@detail_docs(SolicitacaoDoacaoSerializer, "solicitacao-doacao")
@api_view(["GET", "DELETE"])
def view_solicitacao_doacao_detail(request, id):
    try:
        solicitacao_obj = SolicitacaoDoacao.objects.get(pk=id)
        if request.method == "GET":
            serializer = SolicitacaoDoacaoSerializer(solicitacao_obj)
            return Response(
                {"msg": "Successfully retrieved data", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        elif request.method == "DELETE":
            solicitacao_obj.delete()
            return Response(
                {"msg": "SolicitacaoDoacao deleted successfully"}, status=status.HTTP_204_NO_CONTENT
            )
    except SolicitacaoDoacao.DoesNotExist:
        return Response({"msg": "SolicitacaoDoacao not found"}, status=status.HTTP_404_NOT_FOUND)


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
            recompute_doacao_expiracao(doacao)
            return Response(
                {"msg": "Alimento deleted successfully"}, status=status.HTTP_204_NO_CONTENT
            )
    except Alimento.DoesNotExist:
        return Response({"msg": "Alimento not found"}, status=status.HTTP_404_NOT_FOUND)


@detail_docs(NotificacaoSerializer, "notificacao")
@api_view(["GET", "DELETE"])
def view_notificacao_detail(request, id):
    try:
        notificacao_obj = Notificacao.objects.get(pk=id)
        if request.method == "GET":
            serializer = NotificacaoSerializer(notificacao_obj)
            return Response(
                {"msg": "Successfully retrieved data", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        elif request.method == "DELETE":
            notificacao_obj.delete()
            return Response(
                {"msg": "Notificacao deleted successfully"}, status=status.HTTP_204_NO_CONTENT
            )
    except Notificacao.DoesNotExist:
        return Response({"msg": "Notificacao not found"}, status=status.HTTP_404_NOT_FOUND)


@detail_docs(AvaliacaoSerializer, "avaliacao")
@api_view(["GET", "DELETE"])
def view_avaliacao_detail(request, id):
    try:
        avaliacao_obj = Avaliacao.objects.get(pk=id)
        if request.method == "GET":
            serializer = AvaliacaoSerializer(avaliacao_obj)
            return Response(
                {"msg": "Successfully retrieved data", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        elif request.method == "DELETE":
            avaliacao_obj.delete()
            return Response(
                {"msg": "Avaliacao deleted successfully"}, status=status.HTTP_204_NO_CONTENT
            )
    except Avaliacao.DoesNotExist:
        return Response({"msg": "Avaliacao not found"}, status=status.HTTP_404_NOT_FOUND)
