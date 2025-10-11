import pytest
from app.models.ticket import Ticket
from app.models.vehiculo import Vehiculo
from app.models.espacio import Espacio
from app.extensions import db
from datetime import datetime, timezone, timedelta


class TestTransaccionesPages:
    """Pruebas para las páginas HTML de transacciones"""
    
    def test_transacciones_page_loads(self, client):
        """Prueba que la página de transacciones carga"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Acceder a transacciones
        response = client.get('/transacciones')
        
        assert response.status_code == 200
    
    def test_transacciones_page_without_auth(self, client):
        """Prueba que requiere autenticación"""
        response = client.get('/transacciones')
        assert response.status_code in [302, 401]


class TestTransaccionesAPI:
    """Pruebas para la API de transacciones"""
    
    def test_listar_transacciones_vacio(self, client, app):
        """Prueba listar transacciones cuando no hay ninguna"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Listar transacciones
        response = client.get('/api/transacciones')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_listar_transacciones_con_datos(self, client, app):
        """Prueba listar transacciones con tickets finalizados"""
        # Crear varios tickets finalizados
        with app.app_context():
            vehiculo1 = Vehiculo(placa='TRANS001')
            vehiculo2 = Vehiculo(placa='TRANS002')
            
            espacio1 = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            espacio2 = Espacio.query.filter_by(estado='disponible', tipo='moto').all()[0]
            
            db.session.add(vehiculo1)
            db.session.add(vehiculo2)
            db.session.commit()
            
            # Ticket 1 - Finalizado con efectivo
            fecha_entrada1 = datetime.now(timezone.utc) - timedelta(hours=2)
            fecha_salida1 = datetime.now(timezone.utc) - timedelta(hours=1)
            
            ticket1 = Ticket(
                vehiculo_id=vehiculo1.id,
                espacio_id=espacio1.id,
                placa='TRANS001',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=fecha_entrada1,
                fecha_salida=fecha_salida1,
                monto=100.0,
                metodo_pago='efectivo'
            )
            
            # Ticket 2 - Finalizado con tarjeta
            fecha_entrada2 = datetime.now(timezone.utc) - timedelta(hours=3)
            fecha_salida2 = datetime.now(timezone.utc) - timedelta(minutes=30)
            
            ticket2 = Ticket(
                vehiculo_id=vehiculo2.id,
                espacio_id=espacio2.id,
                placa='TRANS002',
                tipo_vehiculo='moto',
                estado='finalizado',
                fecha_entrada=fecha_entrada2,
                fecha_salida=fecha_salida2,
                monto=75.0,
                metodo_pago='tarjeta'
            )
            
            # Ticket 3 - Activo (NO debe aparecer)
            ticket3 = Ticket(
                vehiculo_id=vehiculo1.id,
                espacio_id=espacio1.id,
                placa='TRANS003',
                tipo_vehiculo='regular',
                estado='activo',
                fecha_entrada=datetime.now(timezone.utc)
            )
            
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.add(ticket3)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Listar transacciones
        response = client.get('/api/transacciones')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Solo deben aparecer los 2 tickets finalizados
        assert len(data) == 2
        
        # Verificar que todos tienen estado finalizado
        for transaccion in data:
            assert transaccion['estado'] == 'finalizado'
            assert transaccion['monto'] > 0
            assert transaccion['metodo_pago'] in ['efectivo', 'tarjeta']
            assert 'tiempo_estancia' in transaccion
            assert 'monto_formateado' in transaccion
            assert 'RD$' in transaccion['monto_formateado']
    
    def test_orden_transacciones_por_fecha_desc(self, client, app):
        """Prueba que las transacciones se ordenan por fecha descendente"""
        # Crear tickets con diferentes fechas
        with app.app_context():
            vehiculo = Vehiculo(placa='ORDER001')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            # Ticket más antiguo
            ticket1 = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='ORDER001',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=datetime.now(timezone.utc) - timedelta(days=2),
                fecha_salida=datetime.now(timezone.utc) - timedelta(days=2, hours=-1),
                monto=50.0,
                metodo_pago='efectivo'
            )
            
            # Ticket más reciente
            ticket2 = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='ORDER001',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=datetime.now(timezone.utc) - timedelta(hours=1),
                fecha_salida=datetime.now(timezone.utc),
                monto=50.0,
                metodo_pago='tarjeta'
            )
            
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.commit()
            
            ticket1_id = ticket1.id
            ticket2_id = ticket2.id
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Listar transacciones
        response = client.get('/api/transacciones')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # El ticket más reciente debe aparecer primero
        assert data[0]['id'] == ticket2_id
        assert data[1]['id'] == ticket1_id
    
    def test_estadisticas_transacciones(self, client, app):
        """Prueba obtener estadísticas de transacciones"""
        # Crear varios tickets finalizados
        with app.app_context():
            vehiculo = Vehiculo(placa='STAT001')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            # 3 tickets con efectivo
            for i in range(3):
                ticket = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacio.id,
                    placa=f'STAT00{i+1}',
                    tipo_vehiculo='regular',
                    estado='finalizado',
                    fecha_entrada=datetime.now(timezone.utc) - timedelta(hours=2),
                    fecha_salida=datetime.now(timezone.utc) - timedelta(hours=1),
                    monto=50.0,
                    metodo_pago='efectivo'
                )
                db.session.add(ticket)
            
            # 2 tickets con tarjeta
            for i in range(2):
                ticket = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacio.id,
                    placa=f'STAT10{i+1}',
                    tipo_vehiculo='moto',
                    estado='finalizado',
                    fecha_entrada=datetime.now(timezone.utc) - timedelta(hours=2),
                    fecha_salida=datetime.now(timezone.utc) - timedelta(hours=1),
                    monto=25.0,
                    metodo_pago='tarjeta'
                )
                db.session.add(ticket)
            
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener estadísticas
        response = client.get('/api/transacciones/estadisticas')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar estructura
        assert 'total_transacciones' in data
        assert 'total_recaudado' in data
        assert 'total_recaudado_formateado' in data
        assert 'metodos_pago' in data
        assert 'tipos_vehiculo' in data
        
        # Verificar valores
        assert data['total_transacciones'] == 5
        assert data['total_recaudado'] == 200.0  # (3 x 50) + (2 x 25)
        assert 'RD$' in data['total_recaudado_formateado']
        assert data['metodos_pago']['efectivo'] == 3
        assert data['metodos_pago']['tarjeta'] == 2
        assert data['tipos_vehiculo']['regular'] == 3
        assert data['tipos_vehiculo']['moto'] == 2
    
    def test_estadisticas_sin_transacciones(self, client, app):
        """Prueba estadísticas cuando no hay transacciones"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener estadísticas
        response = client.get('/api/transacciones/estadisticas')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['total_transacciones'] == 0
        assert data['total_recaudado'] == 0
        assert data['metodos_pago']['efectivo'] == 0
        assert data['metodos_pago']['tarjeta'] == 0
    
    def test_transaccion_incluye_tiempo_estancia(self, client, app):
        """Prueba que las transacciones incluyen tiempo de estancia calculado"""
        # Crear ticket con tiempo conocido
        with app.app_context():
            vehiculo = Vehiculo(placa='TIME001')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            # Ticket de exactamente 2 horas y 30 minutos
            fecha_entrada = datetime.now(timezone.utc) - timedelta(hours=2, minutes=30)
            fecha_salida = datetime.now(timezone.utc)
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='TIME001',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=fecha_entrada,
                fecha_salida=fecha_salida,
                monto=150.0,
                metodo_pago='efectivo'
            )
            
            db.session.add(ticket)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Listar transacciones
        response = client.get('/api/transacciones')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data) == 1
        transaccion = data[0]
        
        # Verificar tiempo de estancia
        assert 'tiempo_estancia' in transaccion
        assert transaccion['tiempo_estancia']['horas'] == 2
        assert transaccion['tiempo_estancia']['minutos'] == 30
        assert '2h 30m' in transaccion['tiempo_estancia']['texto']
    
    def test_transacciones_sin_autenticacion(self, client):
        """Prueba que las transacciones requieren autenticación"""
        response = client.get('/api/transacciones')
        assert response.status_code == 401
        
        response = client.get('/api/transacciones/estadisticas')
        assert response.status_code == 401

