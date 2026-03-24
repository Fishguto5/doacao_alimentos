# Aplicativo de Doação de Alimentos.

Um site que tem como objetivo facilitar na doação de alimentos no Brasil através de uma plataforma onde usuários podem anunciar doações, enquanto outros usuários podem reinvindicar as doações.   

### **Integrantes**
- 245210, Carlos Miguel Costa Santiago da Conceição

- 251055, Gabriel Cunha Marchetti

- 231528, Vinicius Forato Coracin

- 257111, Guilherme Webster Chamoun

- 260230, Maria Cecília Torres Vianna

# Inicialização do Repositório:

## Crie um ambiente virtual Python:
```
python -m venv .venv
```
Inicialize o Virtual Env através do comando:
```
source .venv/bin/activate       # Para Linux
.\.venv\Scripts\Activate.ps1    # Para Windows
```

## Instale as dependências e Inicialização do Backend:
```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Usando PostgreSQL

O projeto agora aceita PostgreSQL por variáveis de ambiente, com SQLite como fallback. Isso permite começar simples e trocar de banco sem reescrever o backend.

1. Instale o PostgreSQL na sua máquina.
2. Crie um banco de dados com o nome que quiser, por exemplo `doacao_alimentos`.
3. Crie um arquivo `.env` na raiz do projeto com base em `.env.example`.
4. Preencha os dados de acesso do seu banco.
5. Rode as migrations novamente.

Exemplo de `.env`:

```
USE_POSTGRES=true
POSTGRES_DB=doacao_alimentos
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Comandos para aplicar no banco PostgreSQL:

```
python manage.py migrate
python manage.py runserver
```

Se quiser voltar temporariamente para SQLite, basta remover o `.env` ou definir `USE_POSTGRES=false`.

## Inicialização do frontend
```
cd frontend
npm install
npm run dev
```

## Requirements:
Python - 3.14.3+
npm - 10.9.2+