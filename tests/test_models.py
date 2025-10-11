import pytest
from app.models.usuario import Usuario
from app.extensions import db as _db
from werkzeug.security import generate_password_hash, check_password_hash


class TestUsuarioModel:
    """Pruebas para el modelo Usuario"""
    
    def test_create_user(self, app):
        """Prueba crear un usuario"""
        with app.app_context():
            usuario = Usuario(
                nombre_usuario='newuser',
                contraseña=generate_password_hash('newpass'),
                rol='usuario'
            )
            _db.session.add(usuario)
            _db.session.commit()
            
            assert usuario.id is not None
            assert usuario.nombre_usuario == 'newuser'
    
    def test_password_hashing(self, app):
        """Prueba que la contraseña se guarda hasheada"""
        with app.app_context():
            password_plain = 'securepass'
            usuario = Usuario(
                nombre_usuario='hashuser',
                contraseña=generate_password_hash(password_plain),
                rol='usuario'
            )
            
            # Verificar que el hash es diferente al texto plano
            assert usuario.contraseña != password_plain
            
            # Verificar que el hash funciona correctamente
            assert check_password_hash(usuario.contraseña, password_plain) is True
            assert check_password_hash(usuario.contraseña, 'wrongpass') is False
    
    def test_unique_username(self, app):
        """Prueba que el nombre de usuario debe ser único"""
        with app.app_context():
            # Crear primer usuario
            usuario1 = Usuario(
                nombre_usuario='uniqueuser',
                contraseña=generate_password_hash('pass1'),
                rol='usuario'
            )
            _db.session.add(usuario1)
            _db.session.commit()
            
            # Intentar crear otro con el mismo nombre
            usuario2 = Usuario(
                nombre_usuario='uniqueuser',
                contraseña=generate_password_hash('pass2'),
                rol='usuario'
            )
            _db.session.add(usuario2)
            
            # Debería fallar
            with pytest.raises(Exception):
                _db.session.commit()



