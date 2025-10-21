from datetime import datetime, timezone
import bcrypt

def create_user_model(db):
    """Cria o modelo User dinamicamente após a inicialização do db"""
    
    class User(db.Model):
        """
        Modelo User que representa a entidade usuario
        Herda de db.Model pra integração com SQLAlchemy
        """
        
        __tablename__ = 'users'
        
        # Atributos da classe
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        age = db.Column(db.Integer, nullable=True)
        is_active = db.Column(db.Boolean, default=True, nullable=False)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
        def __init__(self, name, email, password, age=None):
            """
            Construtor da classe User
            
            Args:
                name (str): Nome do usuario
                email (str): Email do usuario
                password (str): Senha do usuario (será hasheada)
                age (int, optional): Idade do usuario
            """
            self.name = name
            self.email = email
            self.password_hash = self._hash_password(password)
            self.age = age
            self.is_active = True
    
        def to_dict(self, include_sensitive=False):
            """
            Converte o objeto User pra dicionário
            
            Args:
                include_sensitive (bool): Se deve incluir dados sensiveis
            
            Returns:
                dict: Dicionário com os dados do usuario
            """
            data = {
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'age': self.age,
                'is_active': self.is_active,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
            
            if include_sensitive:
                data['password_hash'] = self.password_hash
                
            return data
    
        def update_from_dict(self, data):
            """
            Atualiza os dados do usuario a partir de um dicionário
            
            Args:
                data (dict): Dados pra atualização
            """
            if 'name' in data:
                self.name = data['name']
            if 'email' in data:
                self.email = data['email']
            if 'age' in data:
                self.age = data['age']
            if 'password' in data:
                self.password_hash = self._hash_password(data['password'])
            if 'is_active' in data:
                self.is_active = data['is_active']
            self.updated_at = datetime.now(timezone.utc)
        
        def _hash_password(self, password):
            """
            Gera hash da senha usando bcrypt
            
            Args:
                password (str): Senha em texto plano
                
            Returns:
                str: Hash da senha
            """
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        def check_password(self, password):
            """
            Verifica se a senha fornecida esta correta
            
            Args:
                password (str): Senha em texto plano
                
            Returns:
                bool: True se a senha estiver correta
            """
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
        @staticmethod
        def validate_data(data, require_password=False):
            """
            Valida os dados de entrada pra criação/atualização de usuario
            
            Args:
                data (dict): Dados pra validação
                require_password (bool): Se a senha é obrigatoria
                
            Returns:
                tuple: (is_valid, error_message)
            """
            if not data:
                return False, "Dados não fornecidos"
            
            # Validação pra criação
            if 'name' not in data or not data['name'].strip():
                return False, "Nome é obrigatório"
            
            if 'email' not in data or not data['email'].strip():
                return False, "Email é obrigatório"
            
            # Validação de formato de email simples
            if '@' not in data['email']:
                return False, "Email deve ter formato válido"
            
            # Validação de senha se obrigatoria
            if require_password:
                if 'password' not in data or not data['password'].strip():
                    return False, "Senha é obrigatória"
                if len(data['password']) < 6:
                    return False, "Senha deve ter pelo menos 6 caracteres"
            
            # Validação de idade se fornecida
            if 'age' in data and data['age'] is not None:
                try:
                    age = int(data['age'])
                    if age < 0 or age > 150:
                        return False, "Idade deve estar entre 0 e 150 anos"
                except (ValueError, TypeError):
                    return False, "Idade deve ser um número válido"
            
            return True, None
    
        def __repr__(self):
            """
            Representação string do objeto User
            
            Returns:
                str: String representando o usuario
            """
            return f'<User {self.name} - {self.email}>'
    
    return User
