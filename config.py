"""
Configurações da aplicação
"""

import os

class Config:
    """Configuração base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///users.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 dias

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False

# Configuração padrão
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
