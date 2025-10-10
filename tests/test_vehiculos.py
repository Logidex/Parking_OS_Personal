import pytest
from app.models.vehiculo import Vehiculo
from app.extensions import db


class TestVehiculosAPI:
    """Pruebas para la API de vehículos (simplificado - solo placa requerida)"""
    
    def test_crear_vehiculo_solo_placa(self, client, app):
        """Prueba crear un vehículo solo con placa (mínimo requerido)"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Crear vehículo solo con placa
        response = client.post('/api/vehiculos', json={
            'placa': 'ABC123'
        })
        
        # Verificar respuesta
        assert response.status_code == 201
        data = response.get_json()
        assert data['vehiculo']['placa'] == 'ABC123'
        assert data['vehiculo']['marca'] is None  # Campos opcionales
        
        # Verificar en la BD
        with app.app_context():
            vehiculo_db = Vehiculo.query.filter_by(placa='ABC123').first()
            assert vehiculo_db is not None
            assert vehiculo_db.placa == 'ABC123'
    
    def test_crear_vehiculo_completo(self, client, app):
        """Prueba crear un vehículo con todos los datos opcionales"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Crear vehículo con datos completos
        response = client.post('/api/vehiculos', json={
            'placa': 'XYZ789',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'color': 'Rojo',
            'propietario': 'Juan Pérez',
            'telefono': '1234567890'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['vehiculo']['placa'] == 'XYZ789'
        assert data['vehiculo']['marca'] == 'Toyota'
    
    def test_normalizar_placa_mayusculas(self, client):
        """Prueba que la placa se normaliza a mayúsculas"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Crear con minúsculas
        response = client.post('/api/vehiculos', json={
            'placa': 'abc123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['vehiculo']['placa'] == 'ABC123'
    
    def test_placa_duplicada(self, client, app):
        """Prueba que no permite placas duplicadas"""
        # Crear primer vehículo
        with app.app_context():
            vehiculo = Vehiculo(placa='DUP123')
            db.session.add(vehiculo)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar duplicado
        response = client.post('/api/vehiculos', json={
            'placa': 'DUP123'
        })
        
        assert response.status_code == 409
    
    def test_listar_vehiculos(self, client, app):
        """Prueba listar vehículos"""
        # Crear vehículos
        with app.app_context():
            vehiculos = [
                Vehiculo(placa='AAA111'),
                Vehiculo(placa='BBB222', marca='Honda'),
                Vehiculo(placa='CCC333', marca='Toyota', modelo='Corolla'),
            ]
            for v in vehiculos:
                db.session.add(v)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Listar
        response = client.get('/api/vehiculos')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 3


class TestVehiculoModel:
    """Pruebas para el modelo de Vehículo"""
    
    def test_crear_vehiculo_solo_placa(self, app):
        """Prueba crear vehículo solo con placa"""
        with app.app_context():
            vehiculo = Vehiculo(placa='TEST123')
            db.session.add(vehiculo)
            db.session.commit()
            
            assert vehiculo.id is not None
            assert vehiculo.placa == 'TEST123'
            assert vehiculo.marca is None
            assert vehiculo.activo is True
    
    def test_to_dict(self, app):
        """Prueba método to_dict()"""
        with app.app_context():
            vehiculo = Vehiculo(
                placa='DICT123',
                marca='Honda'
            )
            
            resultado = vehiculo.to_dict()
            
            assert isinstance(resultado, dict)
            assert resultado['placa'] == 'DICT123'
            assert resultado['marca'] == 'Honda'
            assert resultado['modelo'] is None


