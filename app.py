"""
Aplicação Flask para operações CRUD de usuários
Seguindo padrão MVC e melhores práticas
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Configuração da aplicação
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Inicialização do banco de dados
db = SQLAlchemy(app)

# Importar e criar modelos
from models.user import create_user_model
User = create_user_model(db)

# Importar controladores
from controllers.user_controller import UserController

# Inicializar controlador
user_controller = UserController(User, db)

@app.route('/users', methods=['GET'])
def get_users():
    """Retorna a lista de todos os usuários"""
    return user_controller.get_all_users()

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Retorna os detalhes de um usuário específico"""
    return user_controller.get_user_by_id(user_id)

@app.route('/users', methods=['POST'])
def create_user():
    """Adiciona um novo usuário"""
    data = request.get_json()
    return user_controller.create_user(data)

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Atualiza os dados de um usuário existente"""
    data = request.get_json()
    return user_controller.update_user(user_id, data)

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Remove um usuário"""
    return user_controller.delete_user(user_id)

@app.errorhandler(404)
def not_found(error):
    """Handler para erro 404"""
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erro 500"""
    return jsonify({'error': 'Erro interno do servidor'}), 500

def create_tables():
    """Cria as tabelas do banco de dados"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)
