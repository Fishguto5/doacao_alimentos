# Test Data - JSONs para Validar CRUDs

Esta pasta contém JSONs de exemplo para testar todos os endpoints CRUD implementados.

## Endpoints e Exemplos

### 1. **Usuario** - `/usuario/`
```bash
# GET - Listar todos
curl http://localhost:8000/usuario/

# POST - Criar novo
curl -X POST http://localhost:8000/usuario/ \
  -H "Content-Type: application/json" \
  -d @usuario.json

# PUT - Atualizar completo (requer 'id' no JSON)
curl -X PUT http://localhost:8000/usuario/ \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "nome": "João Silva", "email": "joao@example.com", ...}'

# PATCH - Atualizar parcial (requer 'id' no JSON)
curl -X PATCH http://localhost:8000/usuario/ \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "nome": "Novo Nome"}'

# DELETE - Deletar (requer 'id' no JSON)
curl -X DELETE http://localhost:8000/usuario/ \
  -H "Content-Type: application/json" \
  -d '{"id": 1}'
```

### 2. **Categoria** - `/categoria/`
```bash
curl -X POST http://localhost:8000/categoria/ \
  -H "Content-Type: application/json" \
  -d @categoria.json
```

### 3. **Doacao** - `/doacao/`
```bash
curl -X POST http://localhost:8000/doacao/ \
  -H "Content-Type: application/json" \
  -d @doacao.json
```

### 4. **Alimento** - `/alimento/`
```bash
curl -X POST http://localhost:8000/alimento/ \
  -H "Content-Type: application/json" \
  -d @alimento.json
```

### 5. **SolicitacaoDoacao** - `/solicitacao-doacao/`
```bash
curl -X POST http://localhost:8000/solicitacao-doacao/ \
  -H "Content-Type: application/json" \
  -d @solicitacao_doacao.json
```

### 6. **Notificacao** - `/notificacao/`
```bash
curl -X POST http://localhost:8000/notificacao/ \
  -H "Content-Type: application/json" \
  -d @notificacao.json
```

### 7. **Avaliacao** - `/avaliacao/`
```bash
curl -X POST http://localhost:8000/avaliacao/ \
  -H "Content-Type: application/json" \
  -d @avaliacao.json
```

## Fluxo de Teste Recomendado

1. **Criar Usuário** (POST /usuario/)
   - Cria 2 usuários: um doador (ID 1) e um solicitante (ID 2)

2. **Criar Categoria** (POST /categoria/)
   - Cria uma categoria "Frutas"

3. **Criar Doação** (POST /doacao/)
   - Usa o usuario ID 1 como doador

4. **Criar Alimento** (POST /alimento/)
   - Vincula à categoria e doação criadas

5. **Criar Solicitação** (POST /solicitacao-doacao/)
   - Usuario ID 2 solicita a doação do usuario ID 1

6. **Criar Notificação** (POST /notificacao/)
   - Notifica o doador sobre a solicitação

7. **Criar Avaliação** (POST /avaliacao/)
   - Usuario ID 2 avalia a transação com usuario ID 1

## Testando Atualizações e Deleções

Após criar registros, use os IDs retornados pelos POSTs para testar PUT, PATCH e DELETE adaptando os JSONs com o ID correto.

Exemplo:
```bash
# PATCH para atualizar nome de usuario
curl -X PATCH http://localhost:8000/usuario/ \
  -H "Content-Type: application/json" \
  -d '{"id": 1, "nome": "João Silva Atualizado"}'
```
