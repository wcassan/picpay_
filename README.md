# API Flask - CRUD de Usuarios com JWT e Swagger

Uma aplicação web desenvolvida em Flask pra realizar operações CRUD (Create, Read, Update, Delete) em uma entidade de "Usuario", com persistência de dados em banco SQLite, autenticação JWT e documentação Swagger.

## Características

- **Framework**: Flask com padrão MVC
- **Banco de Dados**: SQLite com SQLAlchemy ORM
- **Autenticação**: JWT (JSON Web Tokens) com Flask-JWT-Extended
- **Documentação**: Swagger/OpenAPI com Flask-RESTX
- **Arquitetura**: Orientação a Objetos
- **Padrões**: Controller, Repository Pattern
- **Testes**: Cobertura completa com testes unitarios
- **Validação**: Validação robusta de dados de entrada
- **Tratamento de Erros**: Respostas padronizadas com códigos HTTP apropriados
- **Segurança**: Hash de senhas com bcrypt

## Estrutura do Projeto

```
Picpay/
├── app.py                 # Aplicação principal Flask
├── init_db.py            # Script de inicializacao do banco
├── config.py             # Configurações da aplicação
├── requirements.txt      # Dependencias do projeto
├── README.md            # Documentação
├── models/
│   └── user.py          # Modelo User (SQLAlchemy)
├── controllers/
│   ├── user_controller.py # Controlador CRUD
│   └── auth_controller.py # Controlador de autenticação
└── tests/
    └── test_user.py     # Testes unitarios
```

## Instalação e Configuração

### 1. Clone o repositorio
```bash
git clone <url-do-repositorio>
cd Picpay
```

### 2. Instale as dependencias
```bash
pip install -r requirements.txt
```

### 3. Inicialize o banco de dados
```bash
python init_db.py
```

### 4. Execute a aplicação
```bash
python app.py
```

A aplicação estará disponível em: `http://localhost:5000`

### 5. Acessar documentação Swagger
Acesse: `http://localhost:5000/docs/`

## Endpoints da API

### Endpoints de Autenticação

#### POST /api/v1/auth/register
Registra um novo usuario.

**Corpo da Requisição:**
```json
{
  "name": "João Silva",
  "email": "joao@email.com",
  "password": "123456",
  "age": 30
}
```

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "name": "João Silva",
      "email": "joao@email.com",
      "age": 30,
      "is_active": true,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Usuario registrado com sucesso"
}
```

#### POST /api/v1/auth/login
Realiza login do usuario.

**Corpo da Requisição:**
```json
{
  "email": "joao@email.com",
  "password": "123456"
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "name": "João Silva",
      "email": "joao@email.com",
      "age": 30,
      "is_active": true,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Login realizado com sucesso"
}
```

#### POST /api/v1/auth/refresh
Renova o token de acesso.

**Headers:**
```
Authorization: Bearer <refresh_token>
```

#### GET /api/v1/auth/me
Retorna dados do usuario atual.

**Headers:**
```
Authorization: Bearer <access_token>
```

#### POST /api/v1/auth/logout
Realiza logout do usuario.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Endpoints de Usuarios (Protegidos por JWT)

**Headers obrigatorios para todos os endpoints:**
```
Authorization: Bearer <access_token>
```

### 1. GET /users
Retorna a lista de todos os usuarios.

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "João Silva",
      "email": "joao.silva@email.com",
      "age": 30,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00"
    }
  ],
  "count": 1
}
```

### 2. GET /users/{id}
Retorna os detalhes de um usuario específico.

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "João Silva",
    "email": "joao.silva@email.com",
    "age": 30,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
}
```

**Resposta de Erro (404):**
```json
{
  "success": false,
  "error": "Usuario nao encontrado"
}
```

### 3. POST /users
Adiciona um novo usuario.

**Corpo da Requisição:**
```json
{
  "name": "Maria Santos",
  "email": "maria.santos@email.com",
  "age": 25
}
```

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Maria Santos",
    "email": "maria.santos@email.com",
    "age": 25,
    "created_at": "2024-01-01T10:05:00",
    "updated_at": "2024-01-01T10:05:00"
  },
  "message": "Usuario criado com sucesso"
}
```

**Resposta de Erro (400):**
```json
{
  "success": false,
  "error": "Nome é obrigatorio"
}
```

**Resposta de Erro (409):**
```json
{
  "success": false,
  "error": "Email ja cadastrado"
}
```

### 4. PUT /users/{id}
Atualiza os dados de um usuario existente.

**Corpo da Requisição:**
```json
{
  "name": "João Silva Santos",
  "age": 31
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "João Silva Santos",
    "email": "joao.silva@email.com",
    "age": 31,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:10:00"
  },
  "message": "Usuario atualizado com sucesso"
}
```

### 5. DELETE /users/{id}
Remove um usuario.

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "João Silva",
    "email": "joao.silva@email.com",
    "age": 30,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  },
  "message": "Usuario removido com sucesso"
}
```

## Testes

Execute os testes unitarios com:

```bash
# Usando unittest
python -m unittest tests.test_user

# Usando pytest (se instalado)
python -m pytest tests/
```

### Cobertura de Testes

Os testes cobrem:
- Criação de usuarios
- Busca de usuarios (todos e por ID)
- Atualização de usuarios
- Remoção de usuarios
- Validação de dados
- Tratamento de erros
- Testes de integração dos endpoints

## Arquitetura e Padrões

### Padrão MVC (Model-View-Controller)
- **Model**: `models/user.py` - Representa a entidade User
- **View**: Respostas JSON da API
- **Controller**: `controllers/user_controller.py` - Lógica de negocio

### Principios SOLID
- **Single Responsibility**: Cada classe tem uma responsabilidade específica
- **Open/Closed**: Extensivel sem modificação do código existente
- **Liskov Substitution**: Herança adequada do SQLAlchemy
- **Interface Segregation**: Interfaces específicas e coesas
- **Dependency Inversion**: Dependência de abstrações, nao implementações

### Validação e Tratamento de Erros
- Validação robusta de dados de entrada
- Códigos HTTP apropriados pra cada situação
- Mensagens de erro descritivas
- Rollback automático em caso de erro

## Comandos Úteis

### Resetar o banco de dados
```bash
python init_db.py reset
```

### Executar em modo debug
```bash
python app.py
```

### Verificar estrutura do banco
```bash
sqlite3 users.db
.tables
.schema users
```

## Validações Implementadas

- **Nome**: Obrigatorio, nao pode ser vazio
- **Email**: Obrigatorio, deve conter '@', unico no sistema
- **Idade**: Opcional, deve estar entre 0 e 150 anos
- **Duplicação**: Verificação de email duplicado
- **Formato**: Validação de tipos de dados



**Desenvolvido com Flask e Python**
