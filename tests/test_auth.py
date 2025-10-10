import pytest
from flask import session

class TestAuth:
    """Suite de pruebas para autenticación"""
    
    def test_login_page_loads(self, client):
        """Prueba que la página de login carga correctamente"""
        response = client.get('/auth/')
        assert response.status_code == 200
        assert b'Parking OS' in response.data
    
    def test_login_success(self, client):
        """Prueba login exitoso"""
        response = client.post('/auth/login', 
            json={
                'nombre_usuario': 'testuser',
                'password': 'testpass'
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['mensaje'] == 'Login exitoso'
        assert data['usuario'] == 'testuser'
    
    def test_login_invalid_username(self, client):
        """Prueba login con usuario inexistente"""
        response = client.post('/auth/login',
            json={
                'nombre_usuario': 'noexiste',
                'password': 'testpass'
            }
        )
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_invalid_password(self, client):
        """Prueba login con contraseña incorrecta"""
        response = client.post('/auth/login',
            json={
                'nombre_usuario': 'testuser',
                'password': 'wrongpass'
            }
        )
        assert response.status_code == 401
    
    def test_logout(self, client):
        """Prueba logout"""
        # Primero hacer login
        client.post('/auth/login',
            json={
                'nombre_usuario': 'testuser',
                'password': 'testpass'
            }
        )
        
        # Luego logout
        response = client.post('/auth/logout')
        assert response.status_code == 200
        data = response.get_json()
        assert data['mensaje'] == 'Logout exitoso'
