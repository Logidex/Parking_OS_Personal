import pytest
from app.models.ticket import Ticket
from app.models.vehiculo import Vehiculo
from app.models.espacio import Espacio
from app.extensions import db
from datetime import datetime, timezone, timedelta


class TestTicketsPages:
    """Pruebas para las páginas HTML de tickets"""
    
    def test_tickets_page_loads(self, client):
        """Prueba que la página de tickets carga"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Acceder a tickets
        response = client.get('/tickets')
        
        assert response.status_code == 200
    
    def test_tickets_page_without_auth(self, client):
        """Prueba que requiere autenticación"""
        response = client.get('/tickets')
        assert response.status_code in [302, 401]


class TestTicketsAPI:
    """Pruebas para la API de tickets (flujo principal del estacionamiento)"""
    
    def test_ingresar_vehiculo_nuevo(self, client, app):
        """Prueba ingresar un vehículo nuevo al estacionamiento"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Ingresar vehículo
        response = client.post('/api/tickets/ingresar', json={
            'placa': 'ING123',
            'tipo_vehiculo': 'regular'
        })
        
        # Verificar respuesta
        assert response.status_code == 201
        data = response.get_json()
        assert 'ticket' in data
        assert 'espacio' in data
        assert data['ticket']['placa'] == 'ING123'
        assert data['espacio']['numero'] is not None
        
        # Verificar en BD
        with app.app_context():
            vehiculo = Vehiculo.query.filter_by(placa='ING123').first()
            assert vehiculo is not None
            
            ticket = Ticket.query.filter_by(placa='ING123', estado='activo').first()
            assert ticket is not None
            assert ticket.vehiculo_id == vehiculo.id
            
            espacio = Espacio.query.filter_by(id=ticket.espacio_id).first()
            assert espacio.estado == 'ocupado'
    
    def test_registrar_salida_con_metodo_pago_efectivo(self, client, app):
        """Prueba registrar salida con método de pago efectivo"""
        # Crear ticket activo
        with app.app_context():
            vehiculo = Vehiculo(placa='EFECTIVO123')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='EFECTIVO123',
                tipo_vehiculo='regular',
                estado='activo',
                fecha_entrada=datetime.now(timezone.utc)
            )
            espacio.estado = 'ocupado'
            
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Registrar salida con método de pago
        response = client.post(f'/api/tickets/{ticket_id}/salida', json={
            'metodo_pago': 'efectivo'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'monto' in data
        assert 'metodo_pago' in data
        assert data['metodo_pago'] == 'efectivo'
        assert 'monto_formateado' in data
        assert 'RD$' in data['monto_formateado']
        
        # Verificar en BD
        with app.app_context():
            ticket_db = Ticket.query.filter_by(id=ticket_id).first()
            assert ticket_db.estado == 'finalizado'
            assert ticket_db.metodo_pago == 'efectivo'
            assert ticket_db.monto > 0
    
    def test_registrar_salida_con_metodo_pago_tarjeta(self, client, app):
        """Prueba registrar salida con método de pago tarjeta"""
        # Crear ticket activo
        with app.app_context():
            vehiculo = Vehiculo(placa='TARJETA123')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='TARJETA123',
                tipo_vehiculo='regular',
                estado='activo',
                fecha_entrada=datetime.now(timezone.utc)
            )
            espacio.estado = 'ocupado'
            
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Registrar salida con tarjeta
        response = client.post(f'/api/tickets/{ticket_id}/salida', json={
            'metodo_pago': 'tarjeta'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['metodo_pago'] == 'tarjeta'
        
        # Verificar en BD
        with app.app_context():
            ticket_db = Ticket.query.filter_by(id=ticket_id).first()
            assert ticket_db.metodo_pago == 'tarjeta'
    
    def test_metodo_pago_invalido_usa_efectivo_por_defecto(self, client, app):
        """Prueba que método de pago inválido usa efectivo por defecto"""
        # Crear ticket activo
        with app.app_context():
            vehiculo = Vehiculo(placa='INVALIDO123')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='INVALIDO123',
                tipo_vehiculo='regular',
                estado='activo',
                fecha_entrada=datetime.now(timezone.utc)
            )
            espacio.estado = 'ocupado'
            
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Registrar salida con método inválido
        response = client.post(f'/api/tickets/{ticket_id}/salida', json={
            'metodo_pago': 'criptomonedas'  # Método inválido
        })
        
        assert response.status_code == 200
        data = response.get_json()
        # Debería usar 'efectivo' por defecto
        assert data['metodo_pago'] == 'efectivo'
    
    def test_formato_moneda_dominicana(self, client, app):
        """Prueba que el monto se formatea como RD$"""
        # Crear ticket activo
        with app.app_context():
            vehiculo = Vehiculo(placa='MONEDA123')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='MONEDA123',
                tipo_vehiculo='regular',
                estado='activo',
                fecha_entrada=datetime.now(timezone.utc)
            )
            espacio.estado = 'ocupado'
            
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Registrar salida
        response = client.post(f'/api/tickets/{ticket_id}/salida', json={
            'metodo_pago': 'efectivo'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verificar formato de moneda
        assert 'monto_formateado' in data
        assert data['monto_formateado'].startswith('RD$')
        assert ',' in data['monto_formateado'] or data['monto'] < 1000  # Tiene comas si es >= 1000
    
    def test_tiempo_transcurrido_calculado_backend(self, client, app):
        """Prueba que el tiempo transcurrido se calcula en el backend"""
        # Crear ticket activo hace 2 horas
        with app.app_context():
            vehiculo = Vehiculo(placa='TIEMPO123')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            # Ticket de hace 2 horas
            fecha_entrada = datetime.now(timezone.utc) - timedelta(hours=2)
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='TIEMPO123',
                tipo_vehiculo='regular',
                estado='activo',
                fecha_entrada=fecha_entrada
            )
            espacio.estado = 'ocupado'
            
            db.session.add(ticket)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Listar tickets activos
        response = client.get('/api/tickets/activos')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Buscar el ticket
        ticket_encontrado = next((t for t in data if t['placa'] == 'TIEMPO123'), None)
        assert ticket_encontrado is not None
        
        # Verificar que tiene tiempo transcurrido
        assert 'tiempo_transcurrido' in ticket_encontrado
        assert 'horas' in ticket_encontrado['tiempo_transcurrido']
        assert ticket_encontrado['tiempo_transcurrido']['horas'] >= 2
    
    def test_asignacion_automatica_espacio_regular(self, client, app):
        """Prueba que asigna automáticamente el espacio regular más cercano"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Ingresar vehículo regular
        response = client.post('/api/tickets/ingresar', json={
            'placa': 'REG001',
            'tipo_vehiculo': 'regular'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verificar que asignó un espacio regular
        with app.app_context():
            ticket = Ticket.query.filter_by(placa='REG001').first()
            espacio = Espacio.query.filter_by(id=ticket.espacio_id).first()
            assert espacio.tipo == 'regular'
            assert espacio.seccion in ['A', 'B']
    
    def test_asignacion_automatica_moto(self, client, app):
        """Prueba que asigna espacio de moto correctamente"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Ingresar moto
        response = client.post('/api/tickets/ingresar', json={
            'placa': 'MOTO001',
            'tipo_vehiculo': 'moto'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verificar que asignó espacio de moto
        with app.app_context():
            ticket = Ticket.query.filter_by(placa='MOTO001').first()
            espacio = Espacio.query.filter_by(id=ticket.espacio_id).first()
            assert espacio.tipo == 'moto'
            assert espacio.seccion == 'D'
    
    def test_calcular_monto_minimo_una_hora(self, client, app):
        """Prueba que el monto mínimo es por 1 hora"""
        from datetime import datetime, timezone, timedelta
    
        # Crear ticket activo reciente (30 minutos)
        with app.app_context():
            vehiculo = Vehiculo(placa='MIN123')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
        
            db.session.add(vehiculo)
            db.session.commit()
        
            # Ticket de hace 30 minutos
            fecha_entrada = datetime.now(timezone.utc) - timedelta(minutes=30)
        
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='MIN123',
                tipo_vehiculo='regular',
                estado='activo',
                fecha_entrada=fecha_entrada
            )
            espacio.estado = 'ocupado'
        
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id
    
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
    
        # Registrar salida
        response = client.post(f'/api/tickets/{ticket_id}/salida', json={
            'metodo_pago': 'efectivo'
        })
    
        assert response.status_code == 200
        data = response.get_json()
    
        # ⭐ ACTUALIZADO: Debería cobrar mínimo 1 hora (RD$50.00 para regular)
        assert data['monto'] == 50.0, f"Se esperaba 50.0, pero se obtuvo {data['monto']}"



class TestTicketModel:
    """Pruebas para el modelo de Ticket"""
    
    def test_crear_ticket_con_metodo_pago(self, app):
        """Prueba crear ticket con método de pago"""
        with app.app_context():
            vehiculo = Vehiculo(placa='TMODEL123')
            espacio = Espacio.query.first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='TMODEL123',
                tipo_vehiculo='regular',
                estado='finalizado',
                monto=50.0,
                metodo_pago='tarjeta'  # Nuevo campo
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            assert ticket.id is not None
            assert ticket.metodo_pago == 'tarjeta'
            assert ticket.monto == 50.0
    
    def test_to_dict_incluye_metodo_pago(self, app):
        """Prueba que to_dict incluye método de pago"""
        with app.app_context():
            vehiculo = Vehiculo(placa='DICT456')
            espacio = Espacio.query.first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='DICT456',
                tipo_vehiculo='moto',
                estado='activo',
                metodo_pago='efectivo'
            )
            
            resultado = ticket.to_dict()
            
            assert isinstance(resultado, dict)
            assert 'metodo_pago' in resultado
            assert resultado['metodo_pago'] == 'efectivo'




