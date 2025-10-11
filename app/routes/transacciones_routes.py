from flask import Blueprint, render_template, jsonify, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.models.ticket import Ticket
from datetime import datetime, timezone

transacciones_bp = Blueprint('transacciones', __name__)


@transacciones_bp.route('/transacciones')
@jwt_required()
def index():
    """Página principal de transacciones"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        
        if not usuario:
            return redirect(url_for('auth.index'))
        
        return render_template('transacciones.html', usuario=usuario, active_page='transacciones')
    except Exception as e:
        print(f"Error en transacciones: {e}")
        return redirect(url_for('auth.index'))


# ===== API ENDPOINTS =====

@transacciones_bp.route('/api/transacciones', methods=['GET'])
@jwt_required()
def listar_transacciones():
    """Listar todas las transacciones (tickets finalizados)"""
    try:
        # Obtener solo tickets finalizados, ordenados por fecha de salida descendente
        tickets = Ticket.query.filter_by(estado='finalizado').order_by(Ticket.fecha_salida.desc()).all()
        
        resultado = []
        for ticket in tickets:
            ticket_dict = ticket.to_dict()
            
            # Calcular tiempo de estancia
            if ticket.fecha_entrada and ticket.fecha_salida:
                fecha_entrada = ticket.fecha_entrada
                fecha_salida = ticket.fecha_salida
                
                # Asegurar timezone
                if fecha_entrada.tzinfo is None:
                    fecha_entrada = fecha_entrada.replace(tzinfo=timezone.utc)
                if fecha_salida.tzinfo is None:
                    fecha_salida = fecha_salida.replace(tzinfo=timezone.utc)
                
                tiempo_estancia = fecha_salida - fecha_entrada
                total_minutos = int(tiempo_estancia.total_seconds() / 60)
                horas = total_minutos // 60
                minutos = total_minutos % 60
                
                ticket_dict['tiempo_estancia'] = {
                    'horas': horas,
                    'minutos': minutos,
                    'texto': f"{horas}h {minutos}m"
                }
            
            # Formatear monto
            if ticket.monto:
                ticket_dict['monto_formateado'] = f"RD${ticket.monto:,.2f}"
            
            # Información del espacio
            if ticket.espacio:
                ticket_dict['espacio'] = {
                    'numero': ticket.espacio.numero,
                    'tipo': ticket.espacio.tipo,
                    'seccion': ticket.espacio.seccion
                }
            
            resultado.append(ticket_dict)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        print(f"❌ Error al listar transacciones: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@transacciones_bp.route('/api/transacciones/estadisticas', methods=['GET'])
@jwt_required()
def estadisticas_transacciones():
    """Obtener estadísticas de transacciones"""
    try:
        tickets_finalizados = Ticket.query.filter_by(estado='finalizado').all()
        
        # Calcular total recaudado
        total_recaudado = sum(ticket.monto for ticket in tickets_finalizados if ticket.monto)
        
        # Contar por método de pago
        efectivo = sum(1 for ticket in tickets_finalizados if ticket.metodo_pago == 'efectivo')
        tarjeta = sum(1 for ticket in tickets_finalizados if ticket.metodo_pago == 'tarjeta')
        
        # Contar por tipo de vehículo
        motos = sum(1 for ticket in tickets_finalizados if ticket.tipo_vehiculo == 'moto')
        regulares = sum(1 for ticket in tickets_finalizados if ticket.tipo_vehiculo == 'regular')
        discapacitados = sum(1 for ticket in tickets_finalizados if ticket.tipo_vehiculo == 'discapacitado')
        
        return jsonify({
            'total_transacciones': len(tickets_finalizados),
            'total_recaudado': total_recaudado,
            'total_recaudado_formateado': f"RD${total_recaudado:,.2f}",
            'metodos_pago': {
                'efectivo': efectivo,
                'tarjeta': tarjeta
            },
            'tipos_vehiculo': {
                'moto': motos,
                'regular': regulares,
                'discapacitado': discapacitados
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
        return jsonify({"error": str(e)}), 500

