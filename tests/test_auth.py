import pytest


class TestAuth:
    """Pruebas para autenticación"""
    
    def test_login_page_loads(self, client):
        """Prueba que la página de login carga"""
        response = client.get('/auth/')
        assert response.status_code == 200
    
    def test_login_success(self, client):
        """Prueba login exitoso"""
        response = client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'mensaje' in data
    
    def test_login_invalid_username(self, client):
        """Prueba login con usuario inválido"""
        response = client.post('/auth/login', json={
            'nombre_usuario': 'noexiste',
            'password': 'testpass'
        })
        assert response.status_code == 401
    
    def test_login_invalid_password(self, client):
        """Prueba login con contraseña incorrecta"""
        response = client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'wrongpass'
        })
        assert response.status_code == 401
    
    def test_logout(self, client):
        """Prueba logout"""
        # Login primero
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Logout
        response = client.post('/auth/logout')
        assert response.status_code == 200
    
    def test_session_info_endpoint(self, client):
        """Prueba que el endpoint de información de sesión funciona"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener info de sesión
        response = client.get('/auth/session-info')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar campos
        assert 'expira_en' in data
        assert 'tiempo_restante_segundos' in data
        assert data['tiempo_restante_segundos'] > 0
    
    def test_session_info_sin_autenticacion(self, client):
        """Prueba que session-info requiere autenticación"""
        response = client.get('/auth/session-info')
        assert response.status_code == 401


