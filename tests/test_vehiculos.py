import pytest
from app.models.vehiculo import Vehiculo
from app.extensions import db


class TestVehiculosPages:
    """Pruebas para las páginas HTML de vehículos"""
    
    def test_vehiculos_page_loads(self, client):
        """Prueba que la página de vehículos carga"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Acceder a la página de vehículos
        response = client.get('/vehiculos')
        
        # Verificar que carga correctamente
        assert response.status_code == 200
        assert b'Lista de Veh' in response.data  # "Vehículos" con encoding
    
    def test_vehiculos_page_without_auth(self, client):
        """Prueba que no puedes ver vehículos sin login"""
        response = client.get('/vehiculos')
        
        # Debería redirigir o denegar acceso
        assert response.status_code in [302, 401]


class TestVehiculosAPI:
    """Pruebas para la API de vehículos"""
    
    def test_crear_vehiculo_exitoso(self, client, app):
        """Prueba crear un vehículo correctamente"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Crear vehículo
        response = client.post('/api/vehiculos', json={
            'placa': 'ABC123',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'color': 'Rojo',
            'tipo': 'sedan',
            'propietario': 'Juan Pérez',
            'telefono': '1234567890'
        })
        
        # Verificar respuesta
        assert response.status_code == 201
        data = response.get_json()
        assert 'mensaje' in data
        assert 'creado' in data['mensaje'].lower()
        assert data['vehiculo']['placa'] == 'ABC123'
        assert data['vehiculo']['marca'] == 'Toyota'
        assert data['vehiculo']['modelo'] == 'Corolla'
        assert data['vehiculo']['color'] == 'Rojo'
        
        # Verificar en la BD
        with app.app_context():
            vehiculo_db = Vehiculo.query.filter_by(placa='ABC123').first()
            assert vehiculo_db is not None
            assert vehiculo_db.marca == 'Toyota'
            assert vehiculo_db.propietario == 'Juan Pérez'
    
    def test_crear_vehiculo_sin_placa(self, client):
        """Prueba que falla si no envías placa"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar crear vehículo SIN placa
        response = client.post('/api/vehiculos', json={
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'color': 'Rojo'
        })
        
        # Debería dar error
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'placa' in data['error'].lower()
    
    def test_crear_vehiculo_placa_duplicada(self, client, app):
        """Prueba que no permite placas duplicadas"""
        # Crear primer vehículo
        with app.app_context():
            vehiculo = Vehiculo(
                placa='XYZ999',
                marca='Honda',
                modelo='Civic',
                color='Azul',
                tipo='sedan'
            )
            db.session.add(vehiculo)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar crear otro con la misma placa
        response = client.post('/api/vehiculos', json={
            'placa': 'XYZ999',
            'marca': 'Mazda',
            'modelo': 'CX-5',
            'color': 'Negro',
            'tipo': 'suv'
        })
        
        # Debería rechazarlo
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
    
    def test_normalizar_placa_mayusculas(self, client, app):
        """Prueba que la placa se normaliza a mayúsculas"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Crear vehículo con placa en minúsculas
        response = client.post('/api/vehiculos', json={
            'placa': 'abc123',  # Minúsculas
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'color': 'Rojo',
            'tipo': 'sedan'
        })
        
        # Verificar que se guardó en mayúsculas
        assert response.status_code == 201
        data = response.get_json()
        assert data['vehiculo']['placa'] == 'ABC123'  # Mayúsculas
    
    def test_listar_vehiculos(self, client, app):
        """Prueba listar todos los vehículos"""
        # Crear varios vehículos de prueba
        with app.app_context():
            vehiculos = [
                Vehiculo(placa='AAA111', marca='Toyota', modelo='Camry', color='Rojo', tipo='sedan'),
                Vehiculo(placa='BBB222', marca='Honda', modelo='Civic', color='Azul', tipo='sedan'),
                Vehiculo(placa='CCC333', marca='Ford', modelo='F150', color='Negro', tipo='pickup'),
            ]
            for v in vehiculos:
                db.session.add(v)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Listar vehículos
        response = client.get('/api/vehiculos')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 3
        assert any(v['placa'] == 'AAA111' for v in data)
        assert any(v['placa'] == 'BBB222' for v in data)
        assert any(v['placa'] == 'CCC333' for v in data)
    
    def test_buscar_vehiculos_por_placa(self, client, app):
        """Prueba buscar vehículos por placa"""
        # Crear vehículos
        with app.app_context():
            vehiculos = [
                Vehiculo(placa='TEST123', marca='Toyota', modelo='Camry', color='Rojo', tipo='sedan'),
                Vehiculo(placa='OTRO456', marca='Honda', modelo='Civic', color='Azul', tipo='sedan'),
            ]
            for v in vehiculos:
                db.session.add(v)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Buscar por placa
        response = client.get('/api/vehiculos?buscar=TEST')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['placa'] == 'TEST123'
    
    def test_obtener_vehiculo_por_id(self, client, app):
        """Prueba obtener un vehículo específico"""
        # Crear vehículo
        with app.app_context():
            vehiculo = Vehiculo(
                placa='GET123',
                marca='Tesla',
                modelo='Model 3',
                color='Blanco',
                tipo='sedan'
            )
            db.session.add(vehiculo)
            db.session.commit()
            vehiculo_id = vehiculo.id
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener vehículo
        response = client.get(f'/api/vehiculos/{vehiculo_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['placa'] == 'GET123'
        assert data['marca'] == 'Tesla'
    
    def test_actualizar_vehiculo(self, client, app):
        """Prueba actualizar datos de un vehículo"""
        # Crear vehículo
        with app.app_context():
            vehiculo = Vehiculo(
                placa='UPD123',
                marca='Nissan',
                modelo='Sentra',
                color='Gris',
                tipo='sedan'
            )
            db.session.add(vehiculo)
            db.session.commit()
            vehiculo_id = vehiculo.id
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Actualizar color y marca
        response = client.put(f'/api/vehiculos/{vehiculo_id}', json={
            'marca': 'Nissan Actualizado',
            'color': 'Verde'
        })
        
        assert response.status_code == 200
        
        # Verificar que se actualizó
        with app.app_context():
            vehiculo_db = Vehiculo.query.filter_by(id=vehiculo_id).first()
            assert vehiculo_db.marca == 'Nissan Actualizado'
            assert vehiculo_db.color == 'Verde'
            assert vehiculo_db.placa == 'UPD123'  # La placa NO cambia
    
    def test_eliminar_vehiculo(self, client, app):
        """Prueba eliminar un vehículo (solo admin)"""
        # Crear vehículo
        with app.app_context():
            vehiculo = Vehiculo(
                placa='DEL123',
                marca='Chevrolet',
                modelo='Spark',
                color='Amarillo',
                tipo='sedan'
            )
            db.session.add(vehiculo)
            db.session.commit()
            vehiculo_id = vehiculo.id
        
        # Login como admin
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Eliminar
        response = client.delete(f'/api/vehiculos/{vehiculo_id}')
        
        assert response.status_code == 200
        
        # Verificar que ya no existe
        with app.app_context():
            vehiculo_db = Vehiculo.query.filter_by(id=vehiculo_id).first()
            assert vehiculo_db is None
    
    def test_obtener_estadisticas(self, client, app):
        """Prueba obtener estadísticas de vehículos"""
        # Crear varios vehículos
        with app.app_context():
            vehiculos = [
                Vehiculo(placa='STAT1', marca='Toyota', modelo='Camry', color='Rojo', tipo='sedan'),
                Vehiculo(placa='STAT2', marca='Honda', modelo='CRV', color='Azul', tipo='suv'),
                Vehiculo(placa='STAT3', marca='Ford', modelo='F150', color='Negro', tipo='pickup'),
                Vehiculo(placa='STAT4', marca='Toyota', modelo='Hilux', color='Blanco', tipo='pickup'),
            ]
            for v in vehiculos:
                db.session.add(v)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener estadísticas
        response = client.get('/api/vehiculos/estadisticas')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 4
        assert 'por_tipo' in data
        assert data['por_tipo']['sedan'] == 1
        assert data['por_tipo']['suv'] == 1
        assert data['por_tipo']['pickup'] == 2


class TestVehiculoModel:
    """Pruebas para el modelo de Vehículo"""
    
    def test_crear_vehiculo_modelo(self, app):
        """Prueba crear instancia del modelo Vehículo"""
        with app.app_context():
            # Crear vehículo
            vehiculo = Vehiculo(
                placa='MODEL123',
                marca='Toyota',
                modelo='Corolla',
                color='Rojo',
                tipo='sedan',
                propietario='Juan Pérez',
                telefono='1234567890'
            )
            db.session.add(vehiculo)
            db.session.commit()
            
            # Verificar que se creó
            assert vehiculo.id is not None
            assert vehiculo.placa == 'MODEL123'
            assert vehiculo.marca == 'Toyota'
            assert vehiculo.activo is True
    
    def test_to_dict_vehiculo(self, app):
        """Prueba método to_dict() del modelo"""
        with app.app_context():
            vehiculo = Vehiculo(
                placa='DICT123',
                marca='Honda',
                modelo='Civic',
                color='Azul',
                tipo='sedan'
            )
            
            resultado = vehiculo.to_dict()
            
            assert isinstance(resultado, dict)
            assert 'placa' in resultado
            assert 'marca' in resultado
            assert 'modelo' in resultado
            assert 'color' in resultado
            assert 'tipo' in resultado
            assert resultado['placa'] == 'DICT123'
    
    def test_vehiculo_repr(self, app):
        """Prueba representación en string del modelo"""
        with app.app_context():
            vehiculo = Vehiculo(
                placa='REPR123',
                marca='Mazda',
                modelo='CX-5',
                color='Negro',
                tipo='suv'
            )
            
            repr_str = repr(vehiculo)
            
            assert 'REPR123' in repr_str
            assert 'Mazda' in repr_str
            assert 'CX-5' in repr_str
