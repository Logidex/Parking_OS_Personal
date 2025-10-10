import pytest
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash, check_password_hash

class TestUsuarioModel:
    """Suite de pruebas para el modelo Usuario"""
    
    def test_create_user(self, app):
        """Prueba crear un usuario"""
        with app.app_context():
            from app.extensions import db
            
            usuario = Usuario(
                nombre_usuario='nuevo_usuario',
                password=generate_password_hash('password123'),
                rol='operador',
                activo=True
            )
            db.session.add(usuario)
            db.session.commit()
            
            # Verificar que se guardó
            usuario_db = Usuario.query.filter_by(nombre_usuario='nuevo_usuario').first()
            assert usuario_db is not None
            assert usuario_db.rol == 'operador'
            assert usuario_db.activo == True
    
    def test_password_hashing(self, app):
        """Prueba que las contraseñas se hashean correctamente"""
        with app.app_context():
            password = 'supersecreta'
            hashed = generate_password_hash(password)
            
            assert hashed != password  # No debe ser igual a la original
            assert check_password_hash(hashed, password)  # Debe verificar correctamente
    
    def test_unique_username(self, app):
        """Prueba que no se pueden crear usuarios con mismo nombre"""
        with app.app_context():
            from app.extensions import db
            from sqlalchemy.exc import IntegrityError
            
            # Ya existe 'testuser' del fixture
            usuario = Usuario(
                nombre_usuario='testuser',
                password=generate_password_hash('otropass'),
                rol='admin',
                activo=True
            )
            db.session.add(usuario)
            
            with pytest.raises(IntegrityError):
                db.session.commit()
