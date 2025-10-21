"""
Aplicação Flask para operações CRUD de usuários
Seguindo padrão MVC e melhores práticas
Inclui documentação Swagger e autenticação JWT
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_restx import Api, Resource, fields, Namespace
from datetime import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da aplicação
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # Tokens expiram em 1 hora

# Inicialização do banco de dados e JWT
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Middleware para corrigir o header Authorization do Swagger
@app.before_request
def fix_authorization_header():
    """Corrige o header Authorization quando vem do Swagger"""
    auth_header = request.headers.get('Authorization')
    if auth_header and not auth_header.startswith('Bearer '):
        # Se o header não tem "Bearer ", adiciona usando environ
        request.environ['HTTP_AUTHORIZATION'] = f'Bearer {auth_header}'

# Configuração da API Swagger
api = Api(
    app,
    version='1.0',
    title='API CRUD de Usuários',
    description='API REST para operações CRUD de usuários com autenticação JWT',
    doc='/docs/',  # URL para documentação Swagger
    prefix='/api/v1',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Digite apenas o token JWT (sem "Bearer")'
        }
    }
)

# Importar e criar modelos
from models.user import create_user_model
User = create_user_model(db)

# Importar controladores
from controllers.user_controller import UserController
from controllers.auth_controller import AuthController

# Inicializar controladores
user_controller = UserController(User, db)
auth_controller = AuthController(User, db)

# Namespaces para organização
auth_ns = Namespace('auth', description='Operações de autenticação')
users_ns = Namespace('users', description='Operações CRUD de usuários')

# Adicionar namespaces à API
api.add_namespace(auth_ns)
api.add_namespace(users_ns)

# Modelos para documentação Swagger
user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='ID único do usuário'),
    'name': fields.String(required=True, description='Nome do usuário'),
    'email': fields.String(required=True, description='Email do usuário'),
    'age': fields.Integer(description='Idade do usuário'),
    'is_active': fields.Boolean(description='Status ativo do usuário'),
    'created_at': fields.DateTime(readonly=True, description='Data de criação'),
    'updated_at': fields.DateTime(readonly=True, description='Data de atualização')
})

user_create_model = api.model('UserCreate', {
    'name': fields.String(required=True, description='Nome do usuário'),
    'email': fields.String(required=True, description='Email do usuário'),
    'password': fields.String(required=True, description='Senha do usuário'),
    'age': fields.Integer(description='Idade do usuário')
})

user_update_model = api.model('UserUpdate', {
    'name': fields.String(description='Nome do usuário'),
    'email': fields.String(description='Email do usuário'),
    'password': fields.String(description='Nova senha do usuário'),
    'age': fields.Integer(description='Idade do usuário'),
    'is_active': fields.Boolean(description='Status ativo do usuário')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='Email do usuário'),
    'password': fields.String(required=True, description='Senha do usuário')
})

register_model = api.model('Register', {
    'name': fields.String(required=True, description='Nome do usuário'),
    'email': fields.String(required=True, description='Email do usuário'),
    'password': fields.String(required=True, description='Senha do usuário'),
    'age': fields.Integer(description='Idade do usuário')
})

# Decorador para autenticação JWT
def jwt_required_decorator(f):
    """Decorador personalizado para JWT"""
    def decorated_function(*args, **kwargs):
        try:
            return jwt_required()(f)(*args, **kwargs)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Token de acesso inválido ou expirado'
            }), 401
    return decorated_function

# Endpoints de Autenticação
@auth_ns.route('/register')
class Register(Resource):
    @api.expect(register_model)
    def post(self):
        """Registra um novo usuário"""
        data = request.get_json()
        return auth_controller.register(data)

@auth_ns.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Realiza login do usuário"""
        data = request.get_json()
        return auth_controller.login(data)

@auth_ns.route('/refresh')
class Refresh(Resource):
    @api.doc(security='Bearer')
    @jwt_required()
    def post(self):
        """Renova o token de acesso"""
        return auth_controller.refresh_token()

@auth_ns.route('/me')
class CurrentUser(Resource):
    @api.doc(security='Bearer')
    @jwt_required()
    def get(self):
        """Retorna dados do usuário atual"""
        return auth_controller.get_current_user()

@auth_ns.route('/logout')
class Logout(Resource):
    @api.doc(security='Bearer')
    @jwt_required()
    def post(self):
        """Realiza logout do usuário"""
        return auth_controller.logout()

# Endpoints de Usuários (protegidos por JWT)
@users_ns.route('/')
class UserList(Resource):
    @api.doc(security='Bearer')
    @jwt_required()
    def get(self):
        """Retorna a lista de todos os usuários"""
        return user_controller.get_all_users()
    
    @api.doc(security='Bearer')
    @api.expect(user_create_model)
    @jwt_required()
    def post(self):
        """Cria um novo usuário (requer autenticação)"""
        data = request.get_json()
        return user_controller.create_user(data)

# Endpoint alternativo para teste sem autenticação global
@users_ns.route('/create')
class UserCreateAlternative(Resource):
    @api.expect(user_create_model)
    def post(self):
        """Cria um novo usuário (token via header manual)"""
        # Verificar token manualmente
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {'msg': 'Missing Authorization Header'}, 401
        
        token = auth_header.split(' ')[1]
        try:
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = decoded_token['sub']
        except Exception as e:
            return {'msg': f'Invalid token: {str(e)}'}, 401
        
        data = request.get_json()
        return user_controller.create_user(data)

@users_ns.route('/<int:user_id>')
class UserDetail(Resource):
    @api.doc(security='Bearer')
    @jwt_required()
    def get(self, user_id):
        """Retorna os detalhes de um usuário específico"""
        return user_controller.get_user_by_id(user_id)
    
    @api.doc(security='Bearer')
    @jwt_required()
    @api.expect(user_update_model)
    def put(self, user_id):
        """Atualiza os dados de um usuário existente"""
        data = request.get_json()
        return user_controller.update_user(user_id, data)
    
    @api.doc(security='Bearer')
    @jwt_required()
    def delete(self, user_id):
        """Remove um usuário"""
        return user_controller.delete_user(user_id)

# Endpoints legados (sem autenticação para compatibilidade)
@app.route('/users', methods=['GET'])
def get_users_legacy():
    """Retorna a lista de todos os usuários (legado)"""
    return user_controller.get_all_users()

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_legacy(user_id):
    """Retorna os detalhes de um usuário específico (legado)"""
    return user_controller.get_user_by_id(user_id)

@app.route('/users', methods=['POST'])
def create_user_legacy():
    """Adiciona um novo usuário (legado)"""
    data = request.get_json()
    return user_controller.create_user(data)

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user_legacy(user_id):
    """Atualiza os dados de um usuário existente (legado)"""
    data = request.get_json()
    return user_controller.update_user(user_id, data)

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user_legacy(user_id):
    """Remove um usuário (legado)"""
    return user_controller.delete_user(user_id)

# Handlers de erro para a API (Flask-RESTX usa @api.errorhandler diferente)

@app.errorhandler(404)
def not_found_legacy(error):
    """Handler para erro 404 (legado)"""
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error_legacy(error):
    """Handler para erro 500 (legado)"""
    return jsonify({'error': 'Erro interno do servidor'}), 500

def create_tables():
    """Cria as tabelas do banco de dados"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)