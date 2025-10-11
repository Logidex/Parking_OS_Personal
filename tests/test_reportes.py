import pytest
from app.models.ticket import Ticket
from app.models.vehiculo import Vehiculo
from app.models.espacio import Espacio
from app.extensions import db
from datetime import datetime, timezone, timedelta


class TestReportesPages:
    """Pruebas para las páginas de reportes"""
    
    def test_reportes_page_loads(self, client):
        """Prueba que la página de reportes carga"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Acceder a reportes
        response = client.get('/reportes')
        
        assert response.status_code == 200
    
    def test_reportes_page_without_auth(self, client):
        """Prueba que reportes requiere autenticación"""
        response = client.get('/reportes')
        assert response.status_code in [302, 401]


class TestReporteIngresos:
    """Pruebas para el reporte de ingresos por período"""
    
    def test_reporte_ingresos_estructura(self, client, app):
        """Prueba la estructura del reporte de ingresos"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/ingresos-periodo')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar estructura
        assert 'hoy' in data
        assert 'semana' in data
        assert 'mes' in data
        
        # Verificar cada período tiene los campos correctos
        for periodo in ['hoy', 'semana', 'mes']:
            assert 'ingresos' in data[periodo]
            assert 'ingresos_formateado' in data[periodo]
            assert 'transacciones' in data[periodo]
            assert 'promedio' in data[periodo]
            assert 'promedio_formateado' in data[periodo]
            assert 'RD$' in data[periodo]['ingresos_formateado']
    
    def test_reporte_ingresos_con_datos(self, client, app):
        """Prueba reporte de ingresos con datos reales"""
        # Crear tickets finalizados de hoy
        with app.app_context():
            vehiculo = Vehiculo(placa='ING001')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            hoy = datetime.now(timezone.utc)
            
            # 3 tickets de hoy
            for i in range(3):
                ticket = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacio.id,
                    placa=f'ING00{i+1}',
                    tipo_vehiculo='regular',
                    estado='finalizado',
                    fecha_entrada=hoy - timedelta(hours=2),
                    fecha_salida=hoy - timedelta(hours=1),
                    monto=100.0,
                    metodo_pago='efectivo'
                )
                db.session.add(ticket)
            
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/ingresos-periodo')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar ingresos de hoy
        assert data['hoy']['ingresos'] == 300.0
        assert data['hoy']['transacciones'] == 3
        assert data['hoy']['promedio'] == 100.0
    
    def test_reporte_ingresos_semana(self, client, app):
        """Prueba cálculo de ingresos de la semana"""
        with app.app_context():
            vehiculo = Vehiculo(placa='SEM001')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            # Ticket de hace 3 días (debe estar en la semana)
            hace_3_dias = datetime.now(timezone.utc) - timedelta(days=3)
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='SEM001',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=hace_3_dias - timedelta(hours=1),
                fecha_salida=hace_3_dias,
                monto=50.0,
                metodo_pago='tarjeta'
            )
            db.session.add(ticket)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/ingresos-periodo')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Debe incluir el ticket de hace 3 días
        assert data['semana']['ingresos'] >= 50.0
        assert data['semana']['transacciones'] >= 1


class TestReporteOcupacion:
    """Pruebas para el reporte de ocupación"""
    
    def test_reporte_ocupacion_estructura(self, client, app):
        """Prueba la estructura del reporte de ocupación"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/ocupacion-espacios')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar estructura
        assert 'uso_por_tipo' in data
        assert 'ocupacion_actual' in data
        assert 'tiempo_promedio_estancia' in data
        assert 'total_usos_historico' in data
        
        # Verificar uso por tipo
        assert 'regular' in data['uso_por_tipo']
        assert 'moto' in data['uso_por_tipo']
        assert 'discapacitado' in data['uso_por_tipo']
        
        # Verificar ocupación actual
        assert 'total' in data['ocupacion_actual']
        assert 'ocupados' in data['ocupacion_actual']
        assert 'disponibles' in data['ocupacion_actual']
        assert 'porcentaje_ocupacion' in data['ocupacion_actual']
    
    def test_reporte_ocupacion_con_datos(self, client, app):
        """Prueba reporte de ocupación con espacios ocupados"""
        with app.app_context():
            vehiculo = Vehiculo(placa='OCC001')
            db.session.add(vehiculo)
            db.session.commit()
            
            # Ocupar algunos espacios
            espacios = Espacio.query.filter_by(estado='disponible', tipo='regular').limit(5).all()
            
            for i, espacio in enumerate(espacios):
                ticket = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacio.id,
                    placa=f'OCC00{i+1}',
                    tipo_vehiculo='regular',
                    estado='activo',
                    fecha_entrada=datetime.now(timezone.utc)
                )
                espacio.estado = 'ocupado'
                db.session.add(ticket)
            
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/ocupacion-espacios')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar que hay espacios ocupados
        assert data['ocupacion_actual']['ocupados'] >= 5
        assert data['ocupacion_actual']['porcentaje_ocupacion'] > 0
    
    def test_reporte_ocupacion_tiempo_promedio(self, client, app):
        """Prueba cálculo de tiempo promedio de estancia"""
        with app.app_context():
            vehiculo = Vehiculo(placa='TIME001')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            # Crear tickets finalizados con diferentes tiempos
            # Ticket 1: 1 hora
            ticket1 = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='TIME001',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=datetime.now(timezone.utc) - timedelta(hours=2),
                fecha_salida=datetime.now(timezone.utc) - timedelta(hours=1),
                monto=50.0,
                metodo_pago='efectivo'
            )
            
            # Ticket 2: 3 horas
            ticket2 = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='TIME002',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=datetime.now(timezone.utc) - timedelta(hours=4),
                fecha_salida=datetime.now(timezone.utc) - timedelta(hours=1),
                monto=150.0,
                metodo_pago='tarjeta'
            )
            
            db.session.add(ticket1)
            db.session.add(ticket2)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/ocupacion-espacios')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Promedio debería ser aproximadamente 2 horas
        assert data['tiempo_promedio_estancia'] > 0
        assert data['tiempo_promedio_estancia'] >= 1.5
        assert data['tiempo_promedio_estancia'] <= 2.5


class TestReporteVehiculosFrecuentes:
    """Pruebas para el reporte de vehículos frecuentes"""
    
    def test_reporte_vehiculos_frecuentes_vacio(self, client, app):
        """Prueba reporte sin vehículos"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/vehiculos-frecuentes')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_reporte_vehiculos_frecuentes_con_datos(self, client, app):
        """Prueba reporte con vehículos frecuentes"""
        with app.app_context():
            # Crear 3 vehículos
            vehiculo1 = Vehiculo(placa='FREC001', marca='Toyota', modelo='Corolla')
            vehiculo2 = Vehiculo(placa='FREC002', marca='Honda', modelo='Civic')
            vehiculo3 = Vehiculo(placa='FREC003', marca='Nissan', modelo='Sentra')
            
            db.session.add(vehiculo1)
            db.session.add(vehiculo2)
            db.session.add(vehiculo3)
            db.session.commit()
            
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            # Vehículo 1: 5 visitas
            for i in range(5):
                ticket = Ticket(
                    vehiculo_id=vehiculo1.id,
                    espacio_id=espacio.id,
                    placa='FREC001',
                    tipo_vehiculo='regular',
                    estado='finalizado',
                    fecha_entrada=datetime.now(timezone.utc) - timedelta(days=i, hours=2),
                    fecha_salida=datetime.now(timezone.utc) - timedelta(days=i, hours=1),
                    monto=50.0,
                    metodo_pago='efectivo'
                )
                db.session.add(ticket)
            
            # Vehículo 2: 3 visitas
            for i in range(3):
                ticket = Ticket(
                    vehiculo_id=vehiculo2.id,
                    espacio_id=espacio.id,
                    placa='FREC002',
                    tipo_vehiculo='regular',
                    estado='finalizado',
                    fecha_entrada=datetime.now(timezone.utc) - timedelta(days=i, hours=2),
                    fecha_salida=datetime.now(timezone.utc) - timedelta(days=i, hours=1),
                    monto=50.0,
                    metodo_pago='tarjeta'
                )
                db.session.add(ticket)
            
            # Vehículo 3: 1 visita
            ticket = Ticket(
                vehiculo_id=vehiculo3.id,
                espacio_id=espacio.id,
                placa='FREC003',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=datetime.now(timezone.utc) - timedelta(hours=2),
                fecha_salida=datetime.now(timezone.utc) - timedelta(hours=1),
                monto=50.0,
                metodo_pago='efectivo'
            )
            db.session.add(ticket)
            
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/vehiculos-frecuentes')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data) == 3
        
        # Verificar orden (más visitas primero)
        assert data[0]['placa'] == 'FREC001'
        assert data[0]['visitas'] == 5
        assert data[0]['total_gastado'] == 250.0
        
        assert data[1]['placa'] == 'FREC002'
        assert data[1]['visitas'] == 3
        
        assert data[2]['placa'] == 'FREC003'
        assert data[2]['visitas'] == 1
        
        # Verificar formato
        for vehiculo in data:
            assert 'placa' in vehiculo
            assert 'marca' in vehiculo
            assert 'modelo' in vehiculo
            assert 'visitas' in vehiculo
            assert 'total_gastado' in vehiculo
            assert 'total_gastado_formateado' in vehiculo
            assert 'RD$' in vehiculo['total_gastado_formateado']
    
    def test_reporte_vehiculos_limite_10(self, client, app):
        """Prueba que el reporte limita a top 10"""
        with app.app_context():
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            # Crear 15 vehículos con diferentes cantidades de visitas
            for i in range(15):
                vehiculo = Vehiculo(placa=f'LIM{i:03d}')
                db.session.add(vehiculo)
                db.session.commit()
                
                # Cada vehículo tiene i+1 visitas
                for j in range(i + 1):
                    ticket = Ticket(
                        vehiculo_id=vehiculo.id,
                        espacio_id=espacio.id,
                        placa=f'LIM{i:03d}',
                        tipo_vehiculo='regular',
                        estado='finalizado',
                        fecha_entrada=datetime.now(timezone.utc) - timedelta(days=j, hours=2),
                        fecha_salida=datetime.now(timezone.utc) - timedelta(days=j, hours=1),
                        monto=50.0,
                        metodo_pago='efectivo'
                    )
                    db.session.add(ticket)
            
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/vehiculos-frecuentes')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Debe retornar máximo 10
        assert len(data) == 10


class TestReporteMetodosPago:
    """Pruebas para el reporte de métodos de pago"""
    
    def test_reporte_metodos_pago_estructura(self, client, app):
        """Prueba la estructura del reporte de métodos de pago"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/metodos-pago')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar estructura
        assert 'efectivo' in data
        assert 'tarjeta' in data
        assert 'total' in data
        
        # Verificar cada método tiene los campos correctos
        for metodo in ['efectivo', 'tarjeta']:
            assert 'monto' in data[metodo]
            assert 'monto_formateado' in data[metodo]
            assert 'transacciones' in data[metodo]
            assert 'porcentaje' in data[metodo]
            assert 'RD$' in data[metodo]['monto_formateado']
    
    def test_reporte_metodos_pago_con_datos(self, client, app):
        """Prueba reporte con diferentes métodos de pago"""
        with app.app_context():
            vehiculo = Vehiculo(placa='PAG001')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            # 3 tickets con efectivo
            for i in range(3):
                ticket = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacio.id,
                    placa=f'PAG00{i+1}',
                    tipo_vehiculo='regular',
                    estado='finalizado',
                    fecha_entrada=datetime.now(timezone.utc) - timedelta(hours=2),
                    fecha_salida=datetime.now(timezone.utc) - timedelta(hours=1),
                    monto=100.0,
                    metodo_pago='efectivo'
                )
                db.session.add(ticket)
            
            # 2 tickets con tarjeta
            for i in range(2):
                ticket = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacio.id,
                    placa=f'PAG10{i+1}',
                    tipo_vehiculo='regular',
                    estado='finalizado',
                    fecha_entrada=datetime.now(timezone.utc) - timedelta(hours=2),
                    fecha_salida=datetime.now(timezone.utc) - timedelta(hours=1),
                    monto=50.0,
                    metodo_pago='tarjeta'
                )
                db.session.add(ticket)
            
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener reporte
        response = client.get('/api/reportes/metodos-pago')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar efectivo
        assert data['efectivo']['monto'] == 300.0
        assert data['efectivo']['transacciones'] == 3
        assert data['efectivo']['porcentaje'] == 60.0  # 3 de 5
        
        # Verificar tarjeta
        assert data['tarjeta']['monto'] == 100.0
        assert data['tarjeta']['transacciones'] == 2
        assert data['tarjeta']['porcentaje'] == 40.0  # 2 de 5
        
        # Verificar total
        assert data['total']['monto'] == 400.0
        assert data['total']['transacciones'] == 5


class TestReportesAutenticacion:
    """Pruebas de autenticación para reportes"""
    
    def test_todos_reportes_requieren_autenticacion(self, client):
        """Prueba que todos los reportes requieren autenticación"""
        endpoints = [
            '/api/reportes/ingresos-periodo',
            '/api/reportes/ocupacion-espacios',
            '/api/reportes/vehiculos-frecuentes',
            '/api/reportes/metodos-pago'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401, f"{endpoint} no requiere autenticación"
