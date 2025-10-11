import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Base de datos
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'dev_key'
DEBUG = True

# Configuración de JWT
JWT_SECRET_KEY = SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)  # Token expira en 8 horas

# Configuración de cookies JWT
JWT_TOKEN_LOCATION = ['cookies']
JWT_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
JWT_COOKIE_CSRF_PROTECT = False
JWT_ACCESS_COOKIE_PATH = '/'
JWT_COOKIE_SAMESITE = 'Lax'


