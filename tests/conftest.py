import pytest
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.models.espacio import Espacio


@pytest.fixture(scope='function')
def app():
    """Crea una instancia de la aplicación para testing"""
    
    app = create_app()
    
    # Configuración de testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Crear usuario de prueba
        try:
            usuario = Usuario(
                nombre_usuario='testuser',
                contraseña=generate_password_hash('testpass'),
                rol='admin'
            )
            db.session.add(usuario)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️  Error al crear usuario de prueba: {e}")
        
        # Crear espacios de prueba
        espacios_iniciales = []
        
        # Espacios regulares (A y B)
        for seccion in ['A', 'B']:
            for i in range(1, 21):  # 20 por sección
                espacio = Espacio(
                    numero=f'{seccion}-{i:02d}',
                    tipo='regular',
                    estado='disponible',
                    piso=1,
                    seccion=seccion
                )
                espacios_iniciales.append(espacio)
        
        # Espacios para discapacitados (C)
        for i in range(1, 6):  # 5 espacios
            espacio = Espacio(
                numero=f'C-{i:02d}',
                tipo='discapacitado',
                estado='disponible',
                piso=1,
                seccion='C'
            )
            espacios_iniciales.append(espacio)
        
        # Espacios para motos (D)
        for i in range(1, 11):  # 10 espacios
            espacio = Espacio(
                numero=f'D-{i:02d}',
                tipo='moto',
                estado='disponible',
                piso=1,
                seccion='D'
            )
            espacios_iniciales.append(espacio)
        
        try:
            db.session.bulk_save_objects(espacios_iniciales)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️  Error al crear espacios: {e}")
        
        yield app
        
        # ⭐ IMPORTANTE: Limpieza completa después de cada test
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Crea un cliente de prueba para hacer requests"""
    return app.test_client()



    