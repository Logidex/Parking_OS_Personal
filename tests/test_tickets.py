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
            # Vehículo creado
            vehiculo = Vehiculo.query.filter_by(placa='ING123').first()
            assert vehiculo is not None
            
            # Ticket creado
            ticket = Ticket.query.filter_by(placa='ING123', estado='activo').first()
            assert ticket is not None
            assert ticket.vehiculo_id == vehiculo.id
            
            # Espacio marcado como ocupado
            espacio = Espacio.query.filter_by(id=ticket.espacio_id).first()
            assert espacio.estado == 'ocupado'
    
    def test_ingresar_vehiculo_existente(self, client, app):
        """Prueba ingresar un vehículo que ya existe en la BD"""
        # Crear vehículo previamente
        with app.app_context():
            vehiculo = Vehiculo(placa='EXIST123', marca='Toyota')
            db.session.add(vehiculo)
            db.session.commit()
            vehiculo_id = vehiculo.id
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Ingresar vehículo existente
        response = client.post('/api/tickets/ingresar', json={
            'placa': 'EXIST123',
            'tipo_vehiculo': 'regular'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verificar que usó el vehículo existente
        with app.app_context():
            ticket = Ticket.query.filter_by(placa='EXIST123').first()
            assert ticket.vehiculo_id == vehiculo_id
    
    def test_ingresar_vehiculo_ya_dentro(self, client, app):
        """Prueba que no permite ingresar un vehículo que ya está dentro"""
        # Crear vehículo y ticket activo
        with app.app_context():
            vehiculo = Vehiculo(placa='INSIDE123')
            espacio = Espacio.query.filter_by(estado='disponible').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='INSIDE123',
                tipo_vehiculo='regular',
                estado='activo'
            )
            espacio.estado = 'ocupado'
            
            db.session.add(ticket)
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar ingresar de nuevo
        response = client.post('/api/tickets/ingresar', json={
            'placa': 'INSIDE123',
            'tipo_vehiculo': 'regular'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'ya está' in data['error'].lower()
    
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
            # Debería ser el primero disponible (A-01, A-02, etc.)
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
            assert espacio.seccion == 'D'  # Sección D para motos
    
    def test_asignacion_automatica_discapacitado(self, client, app):
        """Prueba que asigna espacio de discapacitado correctamente"""
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Ingresar con discapacidad
        response = client.post('/api/tickets/ingresar', json={
            'placa': 'DISC001',
            'tipo_vehiculo': 'discapacitado'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verificar que asignó espacio de discapacitado
        with app.app_context():
            ticket = Ticket.query.filter_by(placa='DISC001').first()
            espacio = Espacio.query.filter_by(id=ticket.espacio_id).first()
            assert espacio.tipo == 'discapacitado'
            assert espacio.seccion == 'C'  # Sección C para discapacitados
    
    def test_no_hay_espacios_disponibles(self, client, app):
        """Prueba cuando no hay espacios disponibles"""
        # Ocupar todos los espacios de moto
        with app.app_context():
            espacios_moto = Espacio.query.filter_by(tipo='moto').all()
            for espacio in espacios_moto:
                espacio.estado = 'ocupado'
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar ingresar moto
        response = client.post('/api/tickets/ingresar', json={
            'placa': 'NOSPACE',
            'tipo_vehiculo': 'moto'
        })
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'no hay espacios' in data['error'].lower()
    
    def test_listar_tickets_activos(self, client, app):
        """Prueba listar todos los tickets activos"""
        # Crear tickets activos
        with app.app_context():
            vehiculos = [
                Vehiculo(placa='ACT001'),
                Vehiculo(placa='ACT002'),
                Vehiculo(placa='ACT003'),
            ]
            for v in vehiculos:
                db.session.add(v)
            db.session.commit()
            
            espacios = Espacio.query.filter_by(estado='disponible', tipo='regular').limit(3).all()
            
            for i, vehiculo in enumerate(vehiculos):
                ticket = Ticket(
                    vehiculo_id=vehiculo.id,
                    espacio_id=espacios[i].id,
                    placa=vehiculo.placa,
                    tipo_vehiculo='regular',
                    estado='activo'
                )
                espacios[i].estado = 'ocupado'
                db.session.add(ticket)
            
            db.session.commit()
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Listar activos
        response = client.get('/api/tickets/activos')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 3
        assert all(t['estado'] == 'activo' for t in data)
    
    def test_registrar_salida(self, client, app):
        """Prueba registrar la salida de un vehículo"""
        # Crear ticket activo
        with app.app_context():
            vehiculo = Vehiculo(placa='SALIDA123')
            espacio = Espacio.query.filter_by(estado='disponible', tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='SALIDA123',
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
        response = client.post(f'/api/tickets/{ticket_id}/salida')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'monto' in data
        assert 'tiempo_estancia_horas' in data
        
        # Verificar en BD
        with app.app_context():
            ticket_db = Ticket.query.filter_by(id=ticket_id).first()
            assert ticket_db.estado == 'finalizado'
            assert ticket_db.fecha_salida is not None
            assert ticket_db.monto > 0
            
            # Espacio liberado
            espacio_db = Espacio.query.filter_by(id=ticket_db.espacio_id).first()
            assert espacio_db.estado == 'disponible'
    
    def test_calcular_monto_minimo_una_hora(self, client, app):
        """Prueba que el monto mínimo es por 1 hora"""
        # Crear ticket activo reciente (menos de 1 hora)
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
        response = client.post(f'/api/tickets/{ticket_id}/salida')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Debería cobrar mínimo 1 hora
        assert data['monto'] == 10.0  # 1 hora * $10
    
    def test_no_permitir_finalizar_ticket_ya_finalizado(self, client, app):
        """Prueba que no permite finalizar un ticket ya finalizado"""
        # Crear ticket finalizado
        with app.app_context():
            vehiculo = Vehiculo(placa='FIN123')
            espacio = Espacio.query.filter_by(tipo='regular').first()
            
            db.session.add(vehiculo)
            db.session.commit()
            
            ticket = Ticket(
                vehiculo_id=vehiculo.id,
                espacio_id=espacio.id,
                placa='FIN123',
                tipo_vehiculo='regular',
                estado='finalizado',
                fecha_salida=datetime.now(timezone.utc)
            )
            
            db.session.add(ticket)
            db.session.commit()
            ticket_id = ticket.id
        
        # Login
        client.post('/auth/login', json={
            'nombre_usuario': 'testuser',
            'password': 'testpass'
        })
        
        # Intentar finalizar de nuevo
        response = client.post(f'/api/tickets/{ticket_id}/salida')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'ya fue finalizado' in data['error'].lower()


class TestTicketModel:
    """Pruebas para el modelo de Ticket"""
    
    def test_crear_ticket(self, app):
        """Prueba crear instancia del modelo Ticket"""
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
                estado='activo'
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            assert ticket.id is not None
            assert ticket.placa == 'TMODEL123'
            assert ticket.estado == 'activo'
            assert ticket.fecha_entrada is not None
    
    def test_to_dict_ticket(self, app):
        """Prueba método to_dict() del ticket"""
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
                estado='activo'
            )
            
            resultado = ticket.to_dict()
            
            assert isinstance(resultado, dict)
            assert 'placa' in resultado
            assert 'espacio_numero' in resultado
            assert resultado['placa'] == 'DICT456'



