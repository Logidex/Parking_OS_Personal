from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.models.espacio import Espacio
from app.models.ticket import Ticket
from app.extensions import db
from datetime import datetime, timezone

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets')
@jwt_required()
def index():
    """Página principal de tickets (vehículos en el estacionamiento)"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        
        if not usuario:
            return redirect(url_for('auth.index'))
        
        return render_template('tickets.html', usuario=usuario, active_page='tickets')
    except Exception as e:
        print(f"Error en tickets: {e}")
        return redirect(url_for('auth.index'))


# ===== API ENDPOINTS =====

@tickets_bp.route('/api/tickets/activos', methods=['GET'])
@jwt_required()
def listar_tickets_activos():
    """Listar todos los tickets activos (vehículos actualmente en el estacionamiento)"""
    try:
        tickets = Ticket.query.filter_by(estado='activo').order_by(Ticket.fecha_entrada.desc()).all()
        
        resultado = []
        for ticket in tickets:
            ticket_dict = ticket.to_dict()
            
            # ⭐ AGREGAR: Calcular tiempo transcurrido en el backend
            if ticket.fecha_entrada:
                fecha_entrada = ticket.fecha_entrada
                if fecha_entrada.tzinfo is None:
                    fecha_entrada = fecha_entrada.replace(tzinfo=timezone.utc)
                
                ahora = datetime.now(timezone.utc)
                tiempo_transcurrido = ahora - fecha_entrada
                
                # Convertir a horas y minutos
                total_minutos = int(tiempo_transcurrido.total_seconds() / 60)
                horas = total_minutos // 60
                minutos = total_minutos % 60
                
                ticket_dict['tiempo_transcurrido'] = {
                    'horas': horas,
                    'minutos': minutos,
                    'texto': f"{horas}h {minutos}m"
                }
            
            # Agregar información del espacio
            if ticket.espacio:
                ticket_dict['espacio'] = {
                    'numero': ticket.espacio.numero,
                    'tipo': ticket.espacio.tipo,
                    'seccion': ticket.espacio.seccion
                }
            resultado.append(ticket_dict)
        
        return jsonify(resultado), 200
    except Exception as e:
        print(f"❌ Error al listar tickets: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



@tickets_bp.route('/api/tickets/ingresar', methods=['POST'])
@jwt_required()
def ingresar_vehiculo():
    """Ingresar un vehículo al estacionamiento (crear ticket)"""
    try:
        data = request.get_json()
        
        # Validar placa
        if not data or not data.get('placa'):
            return jsonify({"error": "La placa es requerida"}), 400
        
        placa = data['placa'].strip().upper()
        tipo_vehiculo = data.get('tipo_vehiculo', 'regular')  # regular, moto, discapacitado
        
        # Buscar o crear vehículo
        vehiculo = Vehiculo.query.filter_by(placa=placa).first()
        if not vehiculo:
            vehiculo = Vehiculo(placa=placa)
            db.session.add(vehiculo)
            db.session.commit()
        
        # Verificar si el vehículo ya está en el estacionamiento
        ticket_existente = Ticket.query.filter_by(
            vehiculo_id=vehiculo.id,
            estado='activo'
        ).first()
        
        if ticket_existente:
            return jsonify({
                "error": f"El vehículo {placa} ya está en el estacionamiento (Espacio {ticket_existente.espacio.numero})"
            }), 400
        
        # Buscar espacio disponible según tipo
        espacio = buscar_espacio_disponible(tipo_vehiculo)
        
        if not espacio:
            return jsonify({
                "error": f"No hay espacios disponibles para {tipo_vehiculo}"
            }), 404
        
        # Crear ticket
        nuevo_ticket = Ticket(
            vehiculo_id=vehiculo.id,
            espacio_id=espacio.id,
            placa=placa,
            tipo_vehiculo=tipo_vehiculo,
            estado='activo'
        )
        
        # Marcar espacio como ocupado
        espacio.estado = 'ocupado'
        
        db.session.add(nuevo_ticket)
        db.session.commit()
        
        return jsonify({
            "mensaje": f"Vehículo {placa} ingresado exitosamente",
            "ticket": nuevo_ticket.to_dict(),
            "espacio": {
                "numero": espacio.numero,
                "tipo": espacio.tipo,
                "seccion": espacio.seccion
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al ingresar vehículo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@tickets_bp.route('/api/tickets/<int:ticket_id>/salida', methods=['POST'])
@jwt_required()
def registrar_salida(ticket_id):
    """Registrar salida de un vehículo (finalizar ticket)"""
    try:
        ticket = Ticket.query.filter_by(id=ticket_id).first()
        
        if not ticket:
            return jsonify({"error": "Ticket no encontrado"}), 404
        
        if ticket.estado != 'activo':
            return jsonify({"error": "El ticket ya fue finalizado"}), 400
        
        # Calcular tiempo de estancia
        fecha_salida = datetime.now(timezone.utc)
        
        # ⭐ FIX: Asegurar que fecha_entrada tenga timezone
        fecha_entrada = ticket.fecha_entrada
        if fecha_entrada.tzinfo is None:
            # Si no tiene timezone, asumimos que es UTC
            fecha_entrada = fecha_entrada.replace(tzinfo=timezone.utc)
        
        tiempo_estancia = fecha_salida - fecha_entrada
        horas = tiempo_estancia.total_seconds() / 3600
        
        # Calcular monto (ejemplo: $10 por hora)
        monto = calcular_monto(horas, ticket.tipo_vehiculo)
        
        # Actualizar ticket
        ticket.fecha_salida = fecha_salida
        ticket.estado = 'finalizado'
        ticket.monto = monto
        
        # Liberar espacio
        if ticket.espacio:
            ticket.espacio.estado = 'disponible'
        
        db.session.commit()
        
        return jsonify({
            "mensaje": "Salida registrada exitosamente",
            "ticket": ticket.to_dict(),
            "tiempo_estancia_horas": round(horas, 2),
            "monto": monto
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al registrar salida: {e}")
        return jsonify({"error": str(e)}), 500



# ===== FUNCIONES AUXILIARES =====

def buscar_espacio_disponible(tipo_vehiculo):
    """
    Busca el espacio disponible más cercano según el tipo de vehículo
    Prioridad: espacios con números más bajos (más cercanos)
    """
    if tipo_vehiculo == 'moto':
        # Buscar en espacios de moto (sección D)
        espacio = Espacio.query.filter_by(
            tipo='moto',
            estado='disponible',
            activo=True
        ).order_by(Espacio.numero).first()
        
    elif tipo_vehiculo == 'discapacitado':
        # Buscar en espacios para discapacitados (sección C)
        espacio = Espacio.query.filter_by(
            tipo='discapacitado',
            estado='disponible',
            activo=True
        ).order_by(Espacio.numero).first()
        
    else:
        # Buscar en espacios regulares (secciones A y B)
        espacio = Espacio.query.filter_by(
            tipo='regular',
            estado='disponible',
            activo=True
        ).order_by(Espacio.seccion, Espacio.numero).first()
    
    return espacio


def calcular_monto(horas, tipo_vehiculo):
    """
    Calcula el monto a cobrar según horas y tipo de vehículo
    """
    # Tarifas por hora
    tarifas = {
        'moto': 5.0,
        'regular': 10.0,
        'discapacitado': 8.0
    }
    
    tarifa_por_hora = tarifas.get(tipo_vehiculo, 10.0)
    
    # Mínimo 1 hora
    if horas < 1:
        horas = 1
    
    # Redondear hacia arriba
    import math
    horas_cobrar = math.ceil(horas)
    
    return horas_cobrar * tarifa_por_hora

