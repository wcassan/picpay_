"""
Controlador AuthController - Gerencia autenticação e autorização
Implementa login, registro e gerenciamento de tokens JWT
"""

from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from datetime import timedelta

class AuthController:
    """
    Controlador responsável por gerenciar autenticação e autorização
    Implementa login, registro e gerenciamento de tokens JWT
    """
    
    def __init__(self, user_model, database):
        """Construtor do controlador"""
        self.User = user_model
        self.db = database
    
    def register(self, data):
        """
        Registra um novo usuário
        
        Args:
            data (dict): Dados do usuário para registro
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Validação dos dados (senha obrigatória para registro)
            is_valid, error_message = self.User.validate_data(data, require_password=True)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_message
                }, 400
            
            # Verificar se email já existe
            existing_user = self.User.query.filter_by(email=data['email']).first()
            if existing_user:
                return {
                    'success': False,
                    'error': 'Email já cadastrado'
                }, 409
            
            # Criar novo usuário
            user = self.User(
                name=data['name'],
                email=data['email'],
                password=data['password'],
                age=data.get('age')
            )
            
            self.db.session.add(user)
            self.db.session.commit()
            
            # Gerar tokens JWT
            access_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(hours=1)
            )
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return {
                'success': True,
                'data': {
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                },
                'message': 'Usuário registrado com sucesso'
            }, 201
            
        except Exception as e:
            self.db.session.rollback()
            return {
                'success': False,
                'error': f'Erro ao registrar usuário: {str(e)}'
            }, 500
    
    def login(self, data):
        """
        Realiza login do usuário
        
        Args:
            data (dict): Dados de login (email e senha)
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            if not data or 'email' not in data or 'password' not in data:
                return {
                    'success': False,
                    'error': 'Email e senha são obrigatórios'
                }, 400
            
            # Buscar usuário por email
            user = self.User.query.filter_by(email=data['email']).first()
            
            if not user or not user.check_password(data['password']):
                return {
                    'success': False,
                    'error': 'Email ou senha inválidos'
                }, 401
            
            if not user.is_active:
                return {
                    'success': False,
                    'error': 'Usuário inativo'
                }, 401
            
            # Gerar tokens JWT
            access_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(hours=1)
            )
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return {
                'success': True,
                'data': {
                    'user': user.to_dict(),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                },
                'message': 'Login realizado com sucesso'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao realizar login: {str(e)}'
            }, 500
    
    def refresh_token(self):
        """
        Renova o token de acesso usando o refresh token
        
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            current_user_id = get_jwt_identity()
            user = self.db.session.get(self.User, int(current_user_id))
            
            if not user or not user.is_active:
                return {
                    'success': False,
                    'error': 'Usuário não encontrado ou inativo'
                }, 401
            
            # Gerar novo access token
            new_access_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(hours=1)
            )
            
            return {
                'success': True,
                'data': {
                    'access_token': new_access_token
                },
                'message': 'Token renovado com sucesso'
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao renovar token: {str(e)}'
            }, 500
    
    def get_current_user(self):
        """
        Retorna os dados do usuário atual autenticado
        
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            current_user_id = get_jwt_identity()
            user = self.db.session.get(self.User, int(current_user_id))
            
            if not user:
                return {
                    'success': False,
                    'error': 'Usuário não encontrado'
                }, 404
            
            return {
                'success': True,
                'data': user.to_dict()
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao buscar usuário: {str(e)}'
            }, 500
    
    def logout(self):
        """
        Realiza logout do usuário (invalidação do token seria feita no frontend)
        
        Returns:
            tuple: (response_data, status_code)
        """
        return {
            'success': True,
            'message': 'Logout realizado com sucesso'
        }, 200