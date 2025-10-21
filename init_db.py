from app import app, db, User

def init_database():
    """Inicializa o banco de dados com tabelas e dados de exemplo"""
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        print(" Tabelas criadas com sucesso!")
        
        # Verificar se ja existem usuarios
        existing_users = User.query.count()
        if existing_users > 0:
            print(f"Banco já possui {existing_users} usuários")
            return
        
        # Criar usuarios de exemplo
        sample_users = [
            User(name="João Silva", email="joao.silva@email.com", password="123456", age=30),
            User(name="Maria Santos", email="maria.santos@email.com", password="123456", age=25),
            User(name="Pedro Costa", email="pedro.costa@email.com", password="123456", age=35),
            User(name="Ana Lima", email="ana.lima@email.com", password="123456", age=28),
            User(name="Carlos Oliveira", email="carlos.oliveira@email.com", password="123456", age=42)
        ]
        
        # Inserir usuarios no banco
        for user in sample_users:
            db.session.add(user)
        
        db.session.commit()
        print(f" {len(sample_users)} usuários de exemplo criados!")
        
        # Mostrar estatisticas
        total_users = User.query.count()
        print(f" Total de usuários no banco: {total_users}")

def reset_database():
    """Remove todas as tabelas e recria o banco"""
    with app.app_context():
        db.drop_all()
        print("  Todas as tabelas removidas!")
        
        db.create_all()
        print(" Banco recriado com sucesso!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset_database()
    else:
        init_database()
    
    print("\n Para executar a aplicação:")
    print("python app.py")
    print("\n Para executar os testes:")
    print("python -m pytest tests/")
    print("ou")
    print("python -m unittest tests.test_user")
