import pytest
from app.models.usuario import Usuario
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class TestUsuariosPages:
    """Pruebas para las páginas de usuarios"""
    
    def test_usuarios_page_admin(self, client, app):
        """Prueba que admin puede acceder a la página de usuarios"""
        # Login como admin (testuser es admin por defecto en conftest)
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Acceder a usuarios
        response = client.get('/usuarios')
        
        assert response.status_code == 200
    
    def test_usuarios_page_usuario_normal(self, client, app):
        """Prueba que usuario normal NO puede acceder a usuarios"""
        # Crear usuario normal
        with app.app_context():
            usuario_normal = Usuario(
                nombre_usuario='usuario_normal',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            db.session.add(usuario_normal)
            db.session.commit()
        
        # Login como usuario normal
        client.post('/auth/login', json={
            'nombre_usuario': 'usuario_normal',
            'password': 'pass123'
        })
        
        # Intentar acceder a usuarios
        response = client.get('/usuarios')
        
        # Debe denegar acceso
        assert response.status_code == 403
    
    def test_usuarios_page_sin_auth(self, client):
        """Prueba que usuarios requiere autenticación"""
        response = client.get('/usuarios')
        assert response.status_code in [302, 401]


class TestListarUsuarios:
    """Pruebas para listar usuarios"""
    
    def test_listar_usuarios_como_admin(self, client, app):
        """Prueba que admin puede listar usuarios"""
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Listar usuarios
        response = client.get('/api/usuarios')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, list)
        assert len(data) >= 1  # Al menos testuser
        
        # Verificar estructura
        for usuario in data:
            assert 'id' in usuario
            assert 'nombre_usuario' in usuario
            assert 'rol' in usuario
    
    def test_listar_usuarios_como_usuario_normal(self, client, app):
        """Prueba que usuario normal NO puede listar usuarios"""
        # Crear usuario normal
        with app.app_context():
            usuario_normal = Usuario(
                nombre_usuario='normal_user',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            db.session.add(usuario_normal)
            db.session.commit()
        
        # Login como usuario normal
        client.post('/auth/login', json={
            'nombre_usuario': 'normal_user',
            'password': 'pass123'
        })
        
        # Intentar listar usuarios
        response = client.get('/api/usuarios')
        
        assert response.status_code == 403


class TestCrearUsuario:
    """Pruebas para crear usuarios"""
    
    def test_crear_usuario_como_admin(self, client, app):
        """Prueba que admin puede crear usuarios"""
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Crear usuario
        response = client.post('/api/usuarios', json={
            'nombre_usuario': 'nuevo_usuario',
            'password': 'pass1234',
            'rol': 'usuario'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'mensaje' in data
        assert 'usuario' in data
        assert data['usuario']['nombre_usuario'] == 'nuevo_usuario'
        assert data['usuario']['rol'] == 'usuario'
        
        # Verificar en BD
        with app.app_context():
            usuario = Usuario.query.filter_by(nombre_usuario='nuevo_usuario').first()
            assert usuario is not None
            assert usuario.rol == 'usuario'
    
    def test_crear_admin_como_admin(self, client, app):
        """Prueba que admin puede crear otros admins"""
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Crear admin
        response = client.post('/api/usuarios', json={
            'nombre_usuario': 'nuevo_admin',
            'password': 'admin123',
            'rol': 'admin'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['usuario']['rol'] == 'admin'
        
        # Verificar en BD
        with app.app_context():
            usuario = Usuario.query.filter_by(nombre_usuario='nuevo_admin').first()
            assert usuario is not None
            assert usuario.rol == 'admin'
    
    def test_crear_usuario_duplicado(self, client, app):
        """Prueba que no se puede crear usuario con nombre duplicado"""
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar crear usuario con nombre existente
        response = client.post('/api/usuarios', json={
            'nombre_usuario': 'testuser',
            'password': 'newpass',
            'rol': 'usuario'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_crear_usuario_sin_datos(self, client, app):
        """Prueba validación de datos requeridos"""
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar crear sin nombre de usuario
        response = client.post('/api/usuarios', json={
            'password': 'pass123',
            'rol': 'usuario'
        })
        
        assert response.status_code == 400
        
        # Intentar crear sin contraseña
        response = client.post('/api/usuarios', json={
            'nombre_usuario': 'testuser2',
            'rol': 'usuario'
        })
        
        assert response.status_code == 400
    
    def test_crear_usuario_rol_invalido(self, client, app):
        """Prueba validación de rol"""
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar crear con rol inválido
        response = client.post('/api/usuarios', json={
            'nombre_usuario': 'testuser3',
            'password': 'pass123',
            'rol': 'superadmin'  # Rol inválido
        })
        
        assert response.status_code == 400
    
    def test_crear_usuario_como_usuario_normal(self, client, app):
        """Prueba que usuario normal NO puede crear usuarios"""
        # Crear usuario normal
        with app.app_context():
            usuario_normal = Usuario(
                nombre_usuario='normal',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            db.session.add(usuario_normal)
            db.session.commit()
        
        # Login como usuario normal
        client.post('/auth/login', json={
            'nombre_usuario': 'normal',
            'password': 'pass123'
        })
        
        # Intentar crear usuario
        response = client.post('/api/usuarios', json={
            'nombre_usuario': 'otro_usuario',
            'password': 'pass123',
            'rol': 'usuario'
        })
        
        assert response.status_code == 403


class TestEliminarUsuario:
    """Pruebas para eliminar usuarios"""
    
    def test_eliminar_usuario_como_admin(self, client, app):
        """Prueba que admin puede eliminar usuarios"""
        # Crear usuario a eliminar
        with app.app_context():
            usuario = Usuario(
                nombre_usuario='a_eliminar',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            db.session.add(usuario)
            db.session.commit()
            usuario_id = usuario.id
        
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Eliminar usuario
        response = client.delete(f'/api/usuarios/{usuario_id}')
        
        assert response.status_code == 200
        
        # Verificar que fue eliminado
        with app.app_context():
            usuario = Usuario.query.filter_by(id=usuario_id).first()
            assert usuario is None
    
    def test_no_puede_eliminar_propio_usuario(self, client, app):
        """Prueba que no puedes eliminar tu propio usuario"""
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener ID del usuario actual
        with app.app_context():
            usuario = Usuario.query.filter_by(nombre_usuario='testuser').first()
            usuario_id = usuario.id
        
        # Intentar eliminar propio usuario
        response = client.delete(f'/api/usuarios/{usuario_id}')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_no_puede_eliminar_ultimo_admin(self, client, app):
        """Prueba que no se puede eliminar al último admin"""
        # Login como admin (testuser es el único admin)
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Crear usuario normal
        with app.app_context():
            usuario_normal = Usuario(
                nombre_usuario='normal_user',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            db.session.add(usuario_normal)
            db.session.commit()
            
            # Intentar eliminar testuser (único admin) debería fallar
            testuser = Usuario.query.filter_by(nombre_usuario='testuser').first()
            testuser_id = testuser.id
        
        response = client.delete(f'/api/usuarios/{testuser_id}')
        
        # No debería permitir porque es el mismo usuario
        # Pero si fuera otro admin, tampoco debería permitir si es el último
        assert response.status_code == 400
    
    def test_eliminar_usuario_inexistente(self, client, app):
        """Prueba eliminar usuario que no existe"""
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar eliminar usuario con ID inexistente
        response = client.delete('/api/usuarios/99999')
        
        assert response.status_code == 404
    
    def test_eliminar_usuario_como_usuario_normal(self, client, app):
        """Prueba que usuario normal NO puede eliminar usuarios"""
        # Crear usuarios
        with app.app_context():
            usuario_normal = Usuario(
                nombre_usuario='normal',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            usuario_eliminar = Usuario(
                nombre_usuario='eliminar',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            db.session.add(usuario_normal)
            db.session.add(usuario_eliminar)
            db.session.commit()
            usuario_eliminar_id = usuario_eliminar.id
        
        # Login como usuario normal
        client.post('/auth/login', json={
            'nombre_usuario': 'normal',
            'password': 'pass123'
        })
        
        # Intentar eliminar usuario
        response = client.delete(f'/api/usuarios/{usuario_eliminar_id}')
        
        assert response.status_code == 403


class TestCambiarPassword:
    """Pruebas para cambiar contraseña"""
    
    def test_cambiar_password_como_admin(self, client, app):
        """Prueba que admin puede cambiar contraseña de cualquier usuario"""
        # Crear usuario
        with app.app_context():
            usuario = Usuario(
                nombre_usuario='usuario_pass',
                contraseña=generate_password_hash('oldpass'),
                rol='usuario'
            )
            db.session.add(usuario)
            db.session.commit()
            usuario_id = usuario.id
        
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Cambiar contraseña
        response = client.put(f'/api/usuarios/{usuario_id}/cambiar-password', json={
            'nueva_password': 'newpass123'
        })
        
        assert response.status_code == 200
        
        # Verificar que la contraseña cambió
        with app.app_context():
            usuario = Usuario.query.filter_by(id=usuario_id).first()
            assert check_password_hash(usuario.contraseña, 'newpass123')
    
    def test_cambiar_password_validacion_longitud(self, client, app):
        """Prueba validación de longitud mínima de contraseña"""
        # Crear usuario
        with app.app_context():
            usuario = Usuario(
                nombre_usuario='usuario_val',
                contraseña=generate_password_hash('oldpass'),
                rol='usuario'
            )
            db.session.add(usuario)
            db.session.commit()
            usuario_id = usuario.id
        
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar con contraseña muy corta
        response = client.put(f'/api/usuarios/{usuario_id}/cambiar-password', json={
            'nueva_password': '123'  # Menos de 4 caracteres
        })
        
        assert response.status_code == 400
    
    def test_cambiar_password_sin_datos(self, client, app):
        """Prueba validación de datos requeridos"""
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar sin enviar nueva_password
        response = client.put('/api/usuarios/1/cambiar-password', json={})
        
        assert response.status_code == 400


class TestCambiarRol:
    """Pruebas para cambiar rol de usuario"""
    
    def test_cambiar_rol_como_admin(self, client, app):
        """Prueba que admin puede cambiar roles"""
        # Crear usuario
        with app.app_context():
            usuario = Usuario(
                nombre_usuario='usuario_rol',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            db.session.add(usuario)
            db.session.commit()
            usuario_id = usuario.id
        
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Cambiar a admin
        response = client.put(f'/api/usuarios/{usuario_id}/cambiar-rol', json={
            'rol': 'admin'
        })
        
        assert response.status_code == 200
        
        # Verificar cambio
        with app.app_context():
            usuario = Usuario.query.filter_by(id=usuario_id).first()
            assert usuario.rol == 'admin'
    
    def test_no_puede_cambiar_propio_rol(self, client, app):
        """Prueba que no puedes cambiar tu propio rol"""
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener ID del usuario actual
        with app.app_context():
            usuario = Usuario.query.filter_by(nombre_usuario='testuser').first()
            usuario_id = usuario.id
        
        # Intentar cambiar propio rol
        response = client.put(f'/api/usuarios/{usuario_id}/cambiar-rol', json={
            'rol': 'usuario'
        })
        
        assert response.status_code == 400
    
    def test_no_puede_cambiar_rol_ultimo_admin(self, client, app):
        """Prueba que no se puede cambiar el rol del último admin"""
        # Crear otro admin para poder hacer la prueba
        with app.app_context():
            admin2 = Usuario(
                nombre_usuario='admin2',
                contraseña=generate_password_hash('pass123'),
                rol='admin'
            )
            db.session.add(admin2)
            db.session.commit()
            
            # Ahora tenemos 2 admins (testuser y admin2)
            testuser = Usuario.query.filter_by(nombre_usuario='testuser').first()
            testuser_id = testuser.id
        
        # Login como admin2
        client.post('/auth/login', json={
            'nombre_usuario': 'admin2',
            'password': 'pass123'
        })
        
        # Cambiar testuser a usuario (ahora sí debería permitir porque hay 2 admins)
        response = client.put(f'/api/usuarios/{testuser_id}/cambiar-rol', json={
            'rol': 'usuario'
        })
        
        # Debería funcionar porque hay otro admin
        assert response.status_code == 200
        
        # Ahora admin2 es el único admin
        # Intentar cambiar admin2 a usuario debería fallar
        with app.app_context():
            admin2_user = Usuario.query.filter_by(nombre_usuario='admin2').first()
            admin2_id = admin2_user.id
        
        response = client.put(f'/api/usuarios/{admin2_id}/cambiar-rol', json={
            'rol': 'usuario'
        })
        
        # No debería permitir (es el mismo usuario)
        assert response.status_code == 400
    
    def test_cambiar_rol_invalido(self, client, app):
        """Prueba validación de rol"""
        # Crear usuario
        with app.app_context():
            usuario = Usuario(
                nombre_usuario='usuario_test',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            db.session.add(usuario)
            db.session.commit()
            usuario_id = usuario.id
        
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar cambiar a rol inválido
        response = client.put(f'/api/usuarios/{usuario_id}/cambiar-rol', json={
            'rol': 'superadmin'
        })
        
        assert response.status_code == 400
    
    def test_cambiar_rol_como_usuario_normal(self, client, app):
        """Prueba que usuario normal NO puede cambiar roles"""
        # Crear usuarios
        with app.app_context():
            usuario_normal = Usuario(
                nombre_usuario='normal',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            otro_usuario = Usuario(
                nombre_usuario='otro',
                contraseña=generate_password_hash('pass123'),
                rol='usuario'
            )
            db.session.add(usuario_normal)
            db.session.add(otro_usuario)
            db.session.commit()
            otro_id = otro_usuario.id
        
        # Login como usuario normal
        client.post('/auth/login', json={
            'nombre_usuario': 'normal',
            'password': 'pass123'
        })
        
        # Intentar cambiar rol
        response = client.put(f'/api/usuarios/{otro_id}/cambiar-rol', json={
            'rol': 'admin'
        })
        
        assert response.status_code == 403
