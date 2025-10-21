"""
Testes unitarios para a aplicação Flask de usuarios
Cobertura completa das operações CRUD
"""

import unittest
import json
import os
import tempfile
from app import app, db, User
from controllers.user_controller import UserController
from controllers.auth_controller import AuthController

class TestUserModel(unittest.TestCase):
    """Testes pro modelo User"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_user_creation(self):
        """Testa a criação de um usuario"""
        with self.app.app_context():
            user = User(name="João Silva", email="joao@email.com", password="123456", age=30)
            db.session.add(user)
            db.session.commit()
            
            self.assertEqual(user.name, "João Silva")
            self.assertEqual(user.email, "joao@email.com")
            self.assertEqual(user.age, 30)
            self.assertIsNotNone(user.id)
            self.assertTrue(user.check_password("123456"))
    
    def test_user_to_dict(self):
        """Testa a conversão do usuario pra dicionário"""
        with self.app.app_context():
            user = User(name="Maria Santos", email="maria@email.com", password="123456", age=25)
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            self.assertEqual(user_dict['name'], "Maria Santos")
            self.assertEqual(user_dict['email'], "maria@email.com")
            self.assertEqual(user_dict['age'], 25)
            self.assertIn('id', user_dict)
            self.assertIn('created_at', user_dict)
            self.assertNotIn('password_hash', user_dict)  # Nao deve incluir senha por padrão
    
    def test_user_validation(self):
        """Testa a validação de dados do usuario"""
        # Dados validos sem senha
        valid_data = {
            'name': 'Pedro Costa',
            'email': 'pedro@email.com',
            'age': 35
        }
        is_valid, error = User.validate_data(valid_data)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Dados validos com senha
        valid_data_with_password = {
            'name': 'Pedro Costa',
            'email': 'pedro@email.com',
            'password': '123456',
            'age': 35
        }
        is_valid, error = User.validate_data(valid_data_with_password, require_password=True)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Dados invalidos - nome vazio
        invalid_data = {
            'name': '',
            'email': 'test@email.com'
        }
        is_valid, error = User.validate_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('Nome é obrigatório', error)
        
        # Dados invalidos - email invalido
        invalid_data = {
            'name': 'Test User',
            'email': 'email-invalido'
        }
        is_valid, error = User.validate_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertIn('Email deve ter formato válido', error)
    
    def test_user_update_from_dict(self):
        """Testa a atualização de usuario a partir de dicionário"""
        with self.app.app_context():
            user = User(name="Ana Lima", email="ana@email.com", password="123456", age=28)
            db.session.add(user)
            db.session.commit()
            
            update_data = {
                'name': 'Ana Lima Silva',
                'age': 29
            }
            
            user.update_from_dict(update_data)
            db.session.commit()
            
            self.assertEqual(user.name, "Ana Lima Silva")
            self.assertEqual(user.age, 29)
            self.assertEqual(user.email, "ana@email.com")  # Nao alterado

class TestUserController(unittest.TestCase):
    """Testes pro controlador UserController"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
            self.controller = UserController(User, db)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_get_all_users_empty(self):
        """Testa busca de todos os usuarios quando nao há usuarios"""
        with self.app.app_context():
            response, status = self.controller.get_all_users()
            
            self.assertEqual(status, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['count'], 0)
            self.assertEqual(len(data['data']), 0)
    
    def test_get_all_users_with_data(self):
        """Testa busca de todos os usuarios com dados"""
        with self.app.app_context():
            # Criar usuarios de teste
            user1 = User(name="User 1", email="user1@email.com", password="123456", age=25)
            user2 = User(name="User 2", email="user2@email.com", password="123456", age=30)
            db.session.add_all([user1, user2])
            db.session.commit()
            
            response, status = self.controller.get_all_users()
            
            self.assertEqual(status, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['count'], 2)
            self.assertEqual(len(data['data']), 2)
    
    def test_get_user_by_id_success(self):
        """Testa busca de usuario por ID com sucesso"""
        with self.app.app_context():
            user = User(name="Test User", email="test@email.com", password="123456", age=25)
            db.session.add(user)
            db.session.commit()
            
            response, status = self.controller.get_user_by_id(user.id)
            
            self.assertEqual(status, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['name'], "Test User")
    
    def test_get_user_by_id_not_found(self):
        """Testa busca de usuario por ID inexistente"""
        with self.app.app_context():
            response, status = self.controller.get_user_by_id(999)
            
            self.assertEqual(status, 404)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('não encontrado', data['error'])
    
    def test_create_user_success(self):
        """Testa criação de usuario com sucesso"""
        with self.app.app_context():
            user_data = {
                'name': 'Novo Usuário',
                'email': 'novo@email.com',
                'password': '123456',
                'age': 25
            }
            
            response, status = self.controller.create_user(user_data)
            
            self.assertEqual(status, 201)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['name'], 'Novo Usuário')
            self.assertIn('criado com sucesso', data['message'])
    
    def test_create_user_invalid_data(self):
        """Testa criação de usuario com dados invalidos"""
        with self.app.app_context():
            invalid_data = {
                'name': '',
                'email': 'invalid-email'
            }
            
            response, status = self.controller.create_user(invalid_data)
            
            self.assertEqual(status, 400)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('obrigatório', data['error'])
    
    def test_create_user_duplicate_email(self):
        """Testa criação de usuario com email duplicado"""
        with self.app.app_context():
            # Criar primeiro usuário
            user = User(name="Primeiro", email="duplicado@email.com", password="123456")
            db.session.add(user)
            db.session.commit()
            
            # Tentar criar segundo usuario com mesmo email
            user_data = {
                'name': 'Segundo',
                'email': 'duplicado@email.com',
                'password': '123456'
            }
            
            response, status = self.controller.create_user(user_data)
            
            self.assertEqual(status, 409)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('já cadastrado', data['error'])
    
    def test_update_user_success(self):
        """Testa atualização de usuario com sucesso"""
        with self.app.app_context():
            user = User(name="Usuário Original", email="original@email.com", password="123456", age=25)
            db.session.add(user)
            db.session.commit()
            
            update_data = {
                'name': 'Usuário Atualizado',
                'age': 30
            }
            
            response, status = self.controller.update_user(user.id, update_data)
            
            self.assertEqual(status, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['name'], 'Usuário Atualizado')
            self.assertEqual(data['data']['age'], 30)
    
    def test_update_user_not_found(self):
        """Testa atualização de usuario inexistente"""
        with self.app.app_context():
            update_data = {'name': 'Teste'}
            
            response, status = self.controller.update_user(999, update_data)
            
            self.assertEqual(status, 404)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('não encontrado', data['error'])
    
    def test_delete_user_success(self):
        """Testa remoção de usuario com sucesso"""
        with self.app.app_context():
            user = User(name="Usuário para Deletar", email="deletar@email.com", password="123456")
            db.session.add(user)
            db.session.commit()
            
            response, status = self.controller.delete_user(user.id)
            
            self.assertEqual(status, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertIn('removido com sucesso', data['message'])
            
            # Verificar se foi realmente removido
            deleted_user = db.session.get(User, user.id)
            self.assertIsNone(deleted_user)
    
    def test_delete_user_not_found(self):
        """Testa remoção de usuario inexistente"""
        with self.app.app_context():
            response, status = self.controller.delete_user(999)
            
            self.assertEqual(status, 404)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('não encontrado', data['error'])

class TestFlaskApp(unittest.TestCase):
    """Testes de integração pra aplicação Flask"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_get_users_endpoint(self):
        """Testa endpoint GET /users"""
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['count'], 0)
    
    def test_create_user_endpoint(self):
        """Testa endpoint POST /users"""
        user_data = {
            'name': 'Teste Endpoint',
            'email': 'endpoint@email.com',
            'password': '123456',
            'age': 25
        }
        
        response = self.client.post('/users', 
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Teste Endpoint')
    
    def test_get_user_by_id_endpoint(self):
        """Testa endpoint GET /users/{id}"""
        # Primeiro criar um usuario
        user_data = {
            'name': 'Usuário Teste',
            'email': 'teste@email.com',
            'password': '123456'
        }
        
        create_response = self.client.post('/users',
                                        data=json.dumps(user_data),
                                        content_type='application/json')
        user_id = json.loads(create_response.data)['data']['id']
        
        # Buscar o usuario criado
        response = self.client.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Usuário Teste')
    
    def test_update_user_endpoint(self):
        """Testa endpoint PUT /users/{id}"""
        # Criar usuário
        user_data = {
            'name': 'Usuário Original',
            'email': 'original@email.com',
            'password': '123456'
        }
        
        create_response = self.client.post('/users',
                                        data=json.dumps(user_data),
                                        content_type='application/json')
        user_id = json.loads(create_response.data)['data']['id']
        
        # Atualizar usuario
        update_data = {
            'name': 'Usuário Atualizado',
            'age': 30
        }
        
        response = self.client.put(f'/users/{user_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['name'], 'Usuário Atualizado')
    
    def test_delete_user_endpoint(self):
        """Testa endpoint DELETE /users/{id}"""
        # Criar usuário
        user_data = {
            'name': 'Usuário para Deletar',
            'email': 'deletar@email.com',
            'password': '123456'
        }
        
        create_response = self.client.post('/users',
                                        data=json.dumps(user_data),
                                        content_type='application/json')
        user_id = json.loads(create_response.data)['data']['id']
        
        # Deletar usuario
        response = self.client.delete(f'/users/{user_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('removido com sucesso', data['message'])

class TestAuthController(unittest.TestCase):
    """Testes pro controlador de autenticação"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with self.app.app_context():
            db.create_all()
            self.controller = AuthController(User, db)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_register_success(self):
        """Testa registro de usuario com sucesso"""
        with self.app.app_context():
            user_data = {
                'name': 'Novo Usuário',
                'email': 'novo@email.com',
                'password': '123456',
                'age': 25
            }
            
            response, status = self.controller.register(user_data)
            
            self.assertEqual(status, 201)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['user']['name'], 'Novo Usuário')
            self.assertIn('access_token', data['data'])
            self.assertIn('refresh_token', data['data'])
    
    def test_register_duplicate_email(self):
        """Testa registro com email duplicado"""
        with self.app.app_context():
            # Criar primeiro usuário
            user = User(name="Primeiro", email="duplicado@email.com", password="123456")
            db.session.add(user)
            db.session.commit()
            
            # Tentar registrar segundo usuario com mesmo email
            user_data = {
                'name': 'Segundo',
                'email': 'duplicado@email.com',
                'password': '123456'
            }
            
            response, status = self.controller.register(user_data)
            
            self.assertEqual(status, 409)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('já cadastrado', data['error'])
    
    def test_login_success(self):
        """Testa login com sucesso"""
        with self.app.app_context():
            # Criar usuario
            user = User(name="Usuário Teste", email="teste@email.com", password="123456")
            db.session.add(user)
            db.session.commit()
            
            # Fazer login
            login_data = {
                'email': 'teste@email.com',
                'password': '123456'
            }
            
            response, status = self.controller.login(login_data)
            
            self.assertEqual(status, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['user']['email'], 'teste@email.com')
            self.assertIn('access_token', data['data'])
    
    def test_login_invalid_credentials(self):
        """Testa login com credenciais invalidas"""
        with self.app.app_context():
            login_data = {
                'email': 'inexistente@email.com',
                'password': '123456'
            }
            
            response, status = self.controller.login(login_data)
            
            self.assertEqual(status, 401)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('inválidos', data['error'])

if __name__ == '__main__':
    unittest.main()
