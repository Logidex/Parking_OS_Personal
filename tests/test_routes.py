import pytest

class TestProtectedRoutes:
    """Suite de pruebas para rutas protegidas"""
    
    def test_dashboard_without_auth(self, client):
        """Prueba acceder al dashboard sin autenticación"""
        response = client.get('/dashboard')
        # Debería redirigir o dar 401
        assert response.status_code in [302, 401]
    
    def test_dashboard_with_auth(self, client):
        """Prueba acceder al dashboard con autenticación"""
        # Hacer login primero
        client.post('/auth/login',
            json={
                'nombre_usuario': 'testuser',
                'password': 'testpass'
            }
        )
        
        # Acceder al dashboard
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Bienvenido' in response.data
