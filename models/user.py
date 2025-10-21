"""
Modelo User - Representa a entidade usuário no banco de dados
Seguindo padrões de orientação a objetos
"""

from datetime import datetime, timezone

def create_user_model(db):
    """Cria o modelo User dinamicamente após a inicialização do db"""
    
    class User(db.Model):
        """
        Modelo User que representa a entidade usuário
        Herda de db.Model para integração com SQLAlchemy
        """
        
        __tablename__ = 'users'
        
        # Atributos da classe
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(120), unique=True, nullable=False)
        age = db.Column(db.Integer, nullable=True)
        created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
        updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
        def __init__(self, name, email, age=None):
            """
            Construtor da classe User
            
            Args:
                name (str): Nome do usuário
                email (str): Email do usuário
                age (int, optional): Idade do usuário
            """
            self.name = name
            self.email = email
            self.age = age
    
        def to_dict(self):
            """
            Converte o objeto User para dicionário
            
            Returns:
                dict: Dicionário com os dados do usuário
            """
            return {
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'age': self.age,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            }
    
        def update_from_dict(self, data):
            """
            Atualiza os dados do usuário a partir de um dicionário
            
            Args:
                data (dict): Dados para atualização
            """
            if 'name' in data:
                self.name = data['name']
            if 'email' in data:
                self.email = data['email']
            if 'age' in data:
                self.age = data['age']
            self.updated_at = datetime.now(timezone.utc)
    
        @staticmethod
        def validate_data(data):
            """
            Valida os dados de entrada para criação/atualização de usuário
            
            Args:
                data (dict): Dados para validação
                
            Returns:
                tuple: (is_valid, error_message)
            """
            if not data:
                return False, "Dados não fornecidos"
            
            # Validação para criação
            if 'name' not in data or not data['name'].strip():
                return False, "Nome é obrigatório"
            
            if 'email' not in data or not data['email'].strip():
                return False, "Email é obrigatório"
            
            # Validação de formato de email simples
            if '@' not in data['email']:
                return False, "Email deve ter formato válido"
            
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
                str: String representando o usuário
            """
            return f'<User {self.name} - {self.email}>'
    
    return User
