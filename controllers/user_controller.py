"""
Controlador UserController - Gerencia as operações CRUD de usuários
Seguindo padrão Controller e princípios SOLID
"""

from flask import jsonify

class UserController:
    """
    Controlador responsável por gerenciar as operações CRUD de usuários
    Implementa o padrão Controller do MVC
    """
    
    def __init__(self, user_model, database):
        """Construtor do controlador"""
        self.User = user_model
        self.db = database
    
    def get_all_users(self):
        """
        Retorna todos os usuários cadastrados
        
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            users = self.User.query.all()
            users_data = [user.to_dict() for user in users]
            
            return {
                'success': True,
                'data': users_data,
                'count': len(users_data)
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao buscar usuários: {str(e)}'
            }, 500
    
    def get_user_by_id(self, user_id):
        """
        Retorna um usuário específico pelo ID
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            user = self.db.session.get(self.User, user_id)
            
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
    
    def create_user(self, data):
        """
        Cria um novo usuário (requer autenticação de admin)
        
        Args:
            data (dict): Dados do usuário
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Validação dos dados (senha obrigatória para criação via admin)
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
            
            return {
                'success': True,
                'data': user.to_dict(),
                'message': 'Usuário criado com sucesso'
            }, 201
            
        except Exception as e:
            self.db.session.rollback()
            return {
                'success': False,
                'error': f'Erro ao criar usuário: {str(e)}'
            }, 500
    
    def update_user(self, user_id, data):
        """
        Atualiza um usuário existente
        
        Args:
            user_id (int): ID do usuário
            data (dict): Dados para atualização
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Buscar usuário
            user = self.db.session.get(self.User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'Usuário não encontrado'
                }, 404
            
            # Validação dos dados (permitir campos opcionais para atualização)
            if not data:
                return {
                    'success': False,
                    'error': 'Dados não fornecidos'
                }, 400
            
            # Validação específica para atualização
            if 'email' in data and '@' not in data['email']:
                return {
                    'success': False,
                    'error': 'Email deve ter formato válido'
                }, 400
            
            if 'age' in data and data['age'] is not None:
                try:
                    age = int(data['age'])
                    if age < 0 or age > 150:
                        return {
                            'success': False,
                            'error': 'Idade deve estar entre 0 e 150 anos'
                        }, 400
                except (ValueError, TypeError):
                    return {
                        'success': False,
                        'error': 'Idade deve ser um número válido'
                    }, 400
            
            # Verificar se email já existe em outro usuário
            if 'email' in data:
                existing_user = self.User.query.filter(
                    self.User.email == data['email'],
                    self.User.id != user_id
                ).first()
                if existing_user:
                    return {
                        'success': False,
                        'error': 'Email já cadastrado por outro usuário'
                    }, 409
            
            # Atualizar usuário
            user.update_from_dict(data)
            self.db.session.commit()
            
            return {
                'success': True,
                'data': user.to_dict(),
                'message': 'Usuário atualizado com sucesso'
            }, 200
            
        except Exception as e:
            self.db.session.rollback()
            return {
                'success': False,
                'error': f'Erro ao atualizar usuário: {str(e)}'
            }, 500
    
    def delete_user(self, user_id):
        """
        Remove um usuário
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            tuple: (response_data, status_code)
        """
        try:
            # Buscar usuário
            user = self.db.session.get(self.User, user_id)
            if not user:
                return {
                    'success': False,
                    'error': 'Usuário não encontrado'
                }, 404
            
            # Salvar dados do usuário antes de deletar para resposta
            user_data = user.to_dict()
            
            # Deletar usuário
            self.db.session.delete(user)
            self.db.session.commit()
            
            return {
                'success': True,
                'data': user_data,
                'message': 'Usuário removido com sucesso'
            }, 200
            
        except Exception as e:
            self.db.session.rollback()
            return {
                'success': False,
                'error': f'Erro ao remover usuário: {str(e)}'
            }, 500