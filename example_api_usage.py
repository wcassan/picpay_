#!/usr/bin/env python3
"""
Exemplo de uso da API Flask - CRUD de Usuários
Demonstra como usar todos os endpoints da API
"""

import requests
import json

# URL base da API
BASE_URL = "http://localhost:5000"

def test_api():
    """Testa todos os endpoints da API"""
    
    print("🚀 Testando API Flask - CRUD de Usuários")
    print("=" * 50)
    
    # 1. GET /users - Listar todos os usuários
    print("\n1. 📋 Listando todos os usuários:")
    response = requests.get(f"{BASE_URL}/users")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 2. POST /users - Criar novo usuário
    print("\n2. ➕ Criando novo usuário:")
    new_user = {
        "name": "Teste API",
        "email": "teste.api@email.com",
        "age": 25
    }
    response = requests.post(f"{BASE_URL}/users", json=new_user)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        user_id = response.json()['data']['id']
        
        # 3. GET /users/{id} - Buscar usuário específico
        print(f"\n3. 🔍 Buscando usuário ID {user_id}:")
        response = requests.get(f"{BASE_URL}/users/{user_id}")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 4. PUT /users/{id} - Atualizar usuário
        print(f"\n4. ✏️ Atualizando usuário ID {user_id}:")
        update_data = {
            "name": "Teste API Atualizado",
            "age": 26
        }
        response = requests.put(f"{BASE_URL}/users/{user_id}", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 5. DELETE /users/{id} - Remover usuário
        print(f"\n5. 🗑️ Removendo usuário ID {user_id}:")
        response = requests.delete(f"{BASE_URL}/users/{user_id}")
        print(f"Status: {response.status_code}")
        print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 6. Teste de validação - Email duplicado
    print("\n6. ⚠️ Testando validação - Email duplicado:")
    duplicate_user = {
        "name": "Usuário Duplicado",
        "email": "joao.silva@email.com",  # Email que já existe
        "age": 30
    }
    response = requests.post(f"{BASE_URL}/users", json=duplicate_user)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 7. Teste de validação - Dados inválidos
    print("\n7. ⚠️ Testando validação - Dados inválidos:")
    invalid_user = {
        "name": "",  # Nome vazio
        "email": "email-invalido"  # Email sem @
    }
    response = requests.post(f"{BASE_URL}/users", json=invalid_user)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 8. Teste de erro - Usuário não encontrado
    print("\n8. ❌ Testando erro - Usuário não encontrado:")
    response = requests.get(f"{BASE_URL}/users/999")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    print("\n✅ Testes concluídos!")
    print("\n💡 Para executar este exemplo:")
    print("1. Certifique-se de que a aplicação está rodando: python app.py")
    print("2. Execute este script: python example_api_usage.py")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API.")
        print("💡 Certifique-se de que a aplicação Flask está rodando em http://localhost:5000")
        print("   Execute: python app.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
