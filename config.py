import os

# Obtener DATABASE_URL de Railway/Render
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Fix para PostgreSQL (Railway usa postgres:// pero SQLAlchemy necesita postgresql://)
if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

# Si no hay DATABASE_URL, usar SQLite (solo para desarrollo local)
if not SQLALCHEMY_DATABASE_URI:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///parking.db'

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Seguridad
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-CAMBIAR-EN-PRODUCCION')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)

# JWT Config
JWT_TOKEN_LOCATION = ['cookies']
JWT_COOKIE_SECURE = True  # Cambiar a True cuando tengas HTTPS
JWT_COOKIE_CSRF_PROTECT = False
JWT_ACCESS_TOKEN_EXPIRES = 3600





