import pytest
from app.models.espacio import Espacio
from app.extensions import db

class TestEspacios:

    def test_crear_espacio_exitoso(self, client, app):
        """Prueba crear un espacio correctamente (como admin)"""
        # 1. Hacer login como admin
        login_response = client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        print(f"\n🔐 Login response: {login_response.status_code}")
        print(f"Login data: {login_response.get_json()}")

        # 2. Crear un espacio nuevo (numero único)
        response = client.post('/api/espacios', json={
            'numero': 'Z-01',
            'tipo': 'regular',
            'estado': 'disponible',
            'piso': 2,
            'seccion': 'Z'
        })

        # ⭐ AGREGAR ESTO para ver el error
        print(f"\n Status Code: {response.status_code}")
        print(f" Response JSON: {response.get_json()}")
        print(f" Response Data: {response.data.decode('utf-8')}")

        # 3. Verificar respuesta exitosa
        assert response.status_code == 201, f"Se esperaba 201 pero se obtuvo {response.status_code}. Error: {response.get_json()}"
        
        data = response.get_json()
        assert data['espacio']['numero'] == 'Z-01'
        assert data['espacio']['tipo'] == 'regular'
        assert data['espacio']['estado'] == 'disponible'
        assert data['espacio']['piso'] == 2
        assert data['espacio']['seccion'] == 'Z'
        
        # 4. Verifica que existe en la BD
        with app.app_context():
            espacio_db = Espacio.query.filter_by(numero='Z-01').first()
            assert espacio_db is not None
            assert espacio_db.seccion == 'Z'

    def test_no_permitir_espacio_duplicado(self, client, app):
        """Prueba que no permite crear espacio con número repetido"""
        # Precondición: Crear espacio directo en la BD
        with app.app_context():
            espacio = Espacio(
                numero='TEST-01',
                tipo='regular',
                estado='disponible',
                piso=1,
                seccion='T'
            )
            db.session.add(espacio)
            db.session.commit()

        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })

        # Intentar crear duplicado
        response = client.post('/api/espacios', json={
            'numero': 'TEST-01',
            'tipo': 'regular',
            'estado': 'disponible',
            'piso': 1,
            'seccion': 'T'
        })

        assert response.status_code == 409 or response.status_code == 400
        data = response.get_json()
        assert 'ya existe' in data.get('error', '')
