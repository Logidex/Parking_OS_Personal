import pytest
from app.models.ticket import Ticket
from app.models.vehiculo import Vehiculo
from app.models.espacio import Espacio
from app.extensions import db
from datetime import datetime, timezone, timedelta


class TestDashboardPages:
    """Pruebas para las páginas del dashboard"""
    
    def test_dashboard_page_loads(self, client):
        """Prueba que la página del dashboard carga"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Acceder al dashboard
        response = client.get('/dashboard')
        
        assert response.status_code == 200
    
    def test_dashboard_page_without_auth(self, client):
        """Prueba que el dashboard requiere autenticación"""
        response = client.get('/dashboard')
        assert response.status_code in [302, 401]


class TestDashboardEstadisticas:
    """Pruebas para las estadísticas del dashboard"""
    
    def test_estadisticas_basicas(self, client, app):
        """Prueba obtener estadísticas básicas del dashboard"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener estadísticas
        response = client.get('/api/dashboard/estadisticas')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar estructura
        assert 'total_vehiculos' in data
        assert 'espacios_ocupados' in data
        assert 'total_espacios' in data
        assert 'porcentaje_ocupacion' in data
        assert 'tickets_activos' in data
        assert 'ingresos_hoy' in data
        assert 'ingresos_hoy_formateado' in data
        assert 'ingresos_mes' in data
        assert 'ingresos_mes_formateado' in data
        assert 'transacciones_hoy' in data
        
        # Verificar formato de moneda
        assert 'RD$' in data['ingresos_hoy_formateado']
        assert 'RD$' in data['ingresos_mes_formateado']
    
    def test_estadisticas_con_datos(self, client, app):
        """Prueba estadísticas con datos reales"""
        # Crear datos de prueba
        with app.app_context():
            # Crear vehículos
            vehiculo1 = Vehiculo(placa='DASH001')
            vehiculo2 = Vehiculo(placa='DASH002')
            vehiculo3 = Vehiculo(placa='DASH003')
            
            db.session.add(vehiculo1)
            db.session.add(vehiculo2)
            db.session.add(vehiculo3)
            db.session.commit()
            
            # Crear tickets activos
            espacio1 = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            espacio2 = Espacio.query.filter_by(estado='disponible', tipo='moto').first()
            
            ticket_activo1 = Ticket(
                vehiculo_id=vehiculo1.id,
                espacio_id=espacio1.id,
                placa='DASH001',
                tipo_vehiculo='regular',
                estado='activo',
                fecha_entrada=datetime.now(timezone.utc)
            )
            
            ticket_activo2 = Ticket(
                vehiculo_id=vehiculo2.id,
                espacio_id=espacio2.id,
                placa='DASH002',
                tipo_vehiculo='moto',
                estado='activo',
                fecha_entrada=datetime.now(timezone.utc)
            )
            
            # Marcar espacios como ocupados
            espacio1.estado = 'ocupado'
            espacio2.estado = 'ocupado'
            
            # Crear ticket finalizado de hoy
            hoy = datetime.now(timezone.utc)
            ticket_finalizado_hoy = Ticket(
                vehiculo_id=vehiculo3.id,
                espacio_id=espacio1.id,
                placa='DASH003',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=hoy - timedelta(hours=2),
                fecha_salida=hoy,
                monto=100.0,
                metodo_pago='efectivo'
            )
            
            db.session.add(ticket_activo1)
            db.session.add(ticket_activo2)
            db.session.add(ticket_finalizado_hoy)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener estadísticas
        response = client.get('/api/dashboard/estadisticas')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar valores
        assert data['total_vehiculos'] == 3
        assert data['espacios_ocupados'] == 2
        assert data['tickets_activos'] == 2
        assert data['ingresos_hoy'] == 100.0
        assert data['transacciones_hoy'] == 1
        assert data['porcentaje_ocupacion'] > 0
    
    def test_ingresos_del_mes(self, client, app):
        """Prueba cálculo de ingresos del mes"""
        with app.app_context():
            vehiculo = Vehiculo(placa='MES001')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            # Ticket de este mes
            este_mes = datetime.now(timezone.utc)
            ticket_mes = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='MES001',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=este_mes - timedelta(hours=1),
                fecha_salida=este_mes,
                monto=50.0,
                metodo_pago='tarjeta'
            )
            
            # Ticket del mes pasado (no debe contarse)
            mes_pasado = datetime.now(timezone.utc) - timedelta(days=35)
            ticket_viejo = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='MES001',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_entrada=mes_pasado - timedelta(hours=1),
                fecha_salida=mes_pasado,
                monto=100.0,
                metodo_pago='efectivo'
            )
            
            db.session.add(ticket_mes)
            db.session.add(ticket_viejo)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener estadísticas
        response = client.get('/api/dashboard/estadisticas')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Solo debe contar el ticket de este mes
        assert data['ingresos_mes'] == 50.0
    
    def test_porcentaje_ocupacion(self, client, app):
        """Prueba cálculo de porcentaje de ocupación"""
        with app.app_context():
            # Obtener total de espacios
            total_espacios = Espacio.query.filter_by(activo=True).count()
            
            # Ocupar algunos espacios
            espacios = Espacio.query.filter_by(estado='disponible', activo=True).limit(5).all()
            vehiculo = Vehiculo(placa='OCC001')
            db.session.add(vehiculo)
            db.session.commit()
            
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
        
        # Obtener estadísticas
        response = client.get('/api/dashboard/estadisticas')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar porcentaje
        esperado = round((5 / total_espacios * 100), 1)
        assert data['porcentaje_ocupacion'] == esperado


class TestDashboardActividadReciente:
    """Pruebas para actividad reciente"""
    
    def test_actividad_reciente_vacio(self, client, app):
        """Prueba actividad reciente sin datos"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener actividad
        response = client.get('/api/dashboard/actividad-reciente')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_actividad_reciente_con_datos(self, client, app):
        """Prueba actividad reciente con tickets"""
        with app.app_context():
            vehiculo = Vehiculo(placa='ACT001')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            # Crear varios tickets
            for i in range(5):
                ticket = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacio.id,
                    placa=f'ACT00{i+1}',
                    tipo_vehiculo='regular',
                    estado='activo' if i % 2 == 0 else 'finalizado',
                    fecha_entrada=datetime.now(timezone.utc) - timedelta(minutes=i*10),
                    fecha_salida=datetime.now(timezone.utc) if i % 2 == 1 else None,
                    monto=50.0 if i % 2 == 1 else None,
                    metodo_pago='efectivo' if i % 2 == 1 else None
                )
                db.session.add(ticket)
            
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener actividad
        response = client.get('/api/dashboard/actividad-reciente')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert len(data) == 5
        
        # Verificar estructura
        for actividad in data:
            assert 'id' in actividad
            assert 'placa' in actividad
            assert 'tipo_vehiculo' in actividad
            assert 'estado' in actividad
            assert 'fecha_entrada' in actividad
            assert 'espacio' in actividad
    
    def test_actividad_reciente_limite_10(self, client, app):
        """Prueba que la actividad reciente solo muestra últimos 10"""
        with app.app_context():
            vehiculo = Vehiculo(placa='LIM001')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            # Crear 15 tickets
            for i in range(15):
                ticket = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacio.id,
                    placa=f'LIM{i:03d}',
                    tipo_vehiculo='regular',
                    estado='activo',
                    fecha_entrada=datetime.now(timezone.utc) - timedelta(minutes=i*5)
                )
                db.session.add(ticket)
            
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener actividad
        response = client.get('/api/dashboard/actividad-reciente')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Solo debe mostrar 10
        assert len(data) == 10


class TestDashboardOcupacionPorTipo:
    """Pruebas para ocupación por tipo de espacio"""
    
    def test_ocupacion_por_tipo_basico(self, client, app):
        """Prueba obtener ocupación por tipo"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener ocupación
        response = client.get('/api/dashboard/ocupacion-por-tipo')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar estructura
        assert 'regular' in data
        assert 'moto' in data
        assert 'discapacitado' in data
        
        # Verificar cada tipo tiene la estructura correcta
        for tipo in ['regular', 'moto', 'discapacitado']:
            assert 'total' in data[tipo]
            assert 'ocupados' in data[tipo]
            assert 'disponibles' in data[tipo]
            assert 'porcentaje' in data[tipo]
    
    def test_ocupacion_por_tipo_con_datos(self, client, app):
        """Prueba ocupación por tipo con espacios ocupados"""
        with app.app_context():
            vehiculo = Vehiculo(placa='TIPO001')
            db.session.add(vehiculo)
            db.session.commit()
            
            # Ocupar algunos espacios regulares
            espacios_regulares = Espacio.query.filter_by(tipo='regular', estado='disponible').limit(3).all()
            for i, espacio in enumerate(espacios_regulares):
                ticket = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacio.id,
                    placa=f'TIPO00{i+1}',
                    tipo_vehiculo='regular',
                    estado='activo',
                    fecha_entrada=datetime.now(timezone.utc)
                )
                espacio.estado = 'ocupado'
                db.session.add(ticket)
            
            # Ocupar una moto
            espacio_moto = Espacio.query.filter_by(tipo='moto', estado='disponible').first()
            if espacio_moto:
                ticket_moto = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacio_moto.id,
                    placa='MOTO001',
                    tipo_vehiculo='moto',
                    estado='activo',
                    fecha_entrada=datetime.now(timezone.utc)
                )
                espacio_moto.estado = 'ocupado'
                db.session.add(ticket_moto)
            
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Obtener ocupación
        response = client.get('/api/dashboard/ocupacion-por-tipo')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar que los espacios ocupados están correctos
        assert data['regular']['ocupados'] == 3
        assert data['moto']['ocupados'] == 1
        assert data['discapacitado']['ocupados'] == 0
        
        # Verificar disponibles
        assert data['regular']['disponibles'] == data['regular']['total'] - 3
        assert data['moto']['disponibles'] == data['moto']['total'] - 1


class TestDashboardAutenticacion:
    """Pruebas de autenticación para el dashboard"""
    
    def test_estadisticas_sin_autenticacion(self, client):
        """Prueba que las estadísticas requieren autenticación"""
        response = client.get('/api/dashboard/estadisticas')
        assert response.status_code == 401
    
    def test_actividad_sin_autenticacion(self, client):
        """Prueba que la actividad requiere autenticación"""
        response = client.get('/api/dashboard/actividad-reciente')
        assert response.status_code == 401
    
    def test_ocupacion_sin_autenticacion(self, client):
        """Prueba que la ocupación requiere autenticación"""
        response = client.get('/api/dashboard/ocupacion-por-tipo')
        assert response.status_code == 401
