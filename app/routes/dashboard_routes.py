from flask import Blueprint, redirect, render_template, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.models.espacio import Espacio
from app.models.ticket import Ticket
from datetime import datetime, timezone, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@jwt_required()
def index():
    """Dashboard principal"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        
        if not usuario:
            return redirect(url_for('auth.index'))
        
        return render_template('dashboard.html', usuario=usuario, active_page='dashboard')
    except Exception as e:
        print(f"Error en dashboard: {e}")
        return redirect(url_for('auth.index'))


# ===== API ENDPOINTS =====

@dashboard_bp.route('/api/dashboard/estadisticas', methods=['GET'])
@jwt_required()
def estadisticas_dashboard():
    """Obtener estadísticas del dashboard"""
    try:
        # Total de vehículos únicos registrados
        total_vehiculos = Vehiculo.query.count()
        
        # Espacios ocupados
        espacios_ocupados = Espacio.query.filter_by(estado='ocupado').count()
        
        # Total de espacios
        total_espacios = Espacio.query.filter_by(activo=True).count()
        
        # Tickets activos (vehículos actualmente en el estacionamiento)
        tickets_activos = Ticket.query.filter_by(estado='activo').count()
        
        # Ingresos de hoy
        hoy_inicio = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        tickets_hoy = Ticket.query.filter(
            Ticket.estado == 'finalizado',
            Ticket.fecha_salida >= hoy_inicio
        ).all()
        
        ingresos_hoy = sum(ticket.monto for ticket in tickets_hoy if ticket.monto)
        
        # Ingresos del mes
        mes_inicio = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        tickets_mes = Ticket.query.filter(
            Ticket.estado == 'finalizado',
            Ticket.fecha_salida >= mes_inicio
        ).all()
        
        ingresos_mes = sum(ticket.monto for ticket in tickets_mes if ticket.monto)
        
        # Ocupación en porcentaje
        porcentaje_ocupacion = (espacios_ocupados / total_espacios * 100) if total_espacios > 0 else 0
        
        return jsonify({
            'total_vehiculos': total_vehiculos,
            'espacios_ocupados': espacios_ocupados,
            'total_espacios': total_espacios,
            'porcentaje_ocupacion': round(porcentaje_ocupacion, 1),
            'tickets_activos': tickets_activos,
            'ingresos_hoy': ingresos_hoy,
            'ingresos_hoy_formateado': f"RD${ingresos_hoy:,.2f}",
            'ingresos_mes': ingresos_mes,
            'ingresos_mes_formateado': f"RD${ingresos_mes:,.2f}",
            'transacciones_hoy': len(tickets_hoy)
        }), 200
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas del dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/api/dashboard/actividad-reciente', methods=['GET'])
@jwt_required()
def actividad_reciente():
    """Obtener actividad reciente (últimos 10 tickets)"""
    try:
        # Obtener los últimos 10 tickets (activos y finalizados)
        tickets = Ticket.query.order_by(Ticket.fecha_entrada.desc()).limit(10).all()
        
        resultado = []
        for ticket in tickets:
            ticket_dict = {
                'id': ticket.id,
                'placa': ticket.placa,
                'tipo_vehiculo': ticket.tipo_vehiculo,
                'estado': ticket.estado,
                'fecha_entrada': ticket.fecha_entrada.isoformat() if ticket.fecha_entrada else None,
                'fecha_salida': ticket.fecha_salida.isoformat() if ticket.fecha_salida else None,
                'monto': ticket.monto,
                'monto_formateado': f"RD${ticket.monto:,.2f}" if ticket.monto else None,
                'metodo_pago': ticket.metodo_pago
            }
            
            # Calcular tiempo transcurrido para tickets activos
            if ticket.estado == 'activo' and ticket.fecha_entrada:
                fecha_entrada = ticket.fecha_entrada
                if fecha_entrada.tzinfo is None:
                    fecha_entrada = fecha_entrada.replace(tzinfo=timezone.utc)
                
                ahora = datetime.now(timezone.utc)
                tiempo_transcurrido = ahora - fecha_entrada
                total_minutos = int(tiempo_transcurrido.total_seconds() / 60)
                horas = total_minutos // 60
                minutos = total_minutos % 60
                
                ticket_dict['tiempo_transcurrido'] = f"{horas}h {minutos}m"
            
            # Información del espacio
            if ticket.espacio:
                ticket_dict['espacio'] = ticket.espacio.numero
            
            resultado.append(ticket_dict)
        
        return jsonify(resultado), 200
        
    except Exception as e:
        print(f"❌ Error al obtener actividad reciente: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route('/api/dashboard/ocupacion-por-tipo', methods=['GET'])
@jwt_required()
def ocupacion_por_tipo():
    """Obtener ocupación por tipo de espacio"""
    try:
        # Espacios regulares
        regulares_total = Espacio.query.filter_by(tipo='regular', activo=True).count()
        regulares_ocupados = Espacio.query.filter_by(tipo='regular', estado='ocupado', activo=True).count()
        
        # Espacios de motos
        motos_total = Espacio.query.filter_by(tipo='moto', activo=True).count()
        motos_ocupados = Espacio.query.filter_by(tipo='moto', estado='ocupado', activo=True).count()
        
        # Espacios discapacitados
        discapacitados_total = Espacio.query.filter_by(tipo='discapacitado', activo=True).count()
        discapacitados_ocupados = Espacio.query.filter_by(tipo='discapacitado', estado='ocupado', activo=True).count()
        
        return jsonify({
            'regular': {
                'total': regulares_total,
                'ocupados': regulares_ocupados,
                'disponibles': regulares_total - regulares_ocupados,
                'porcentaje': round((regulares_ocupados / regulares_total * 100) if regulares_total > 0 else 0, 1)
            },
            'moto': {
                'total': motos_total,
                'ocupados': motos_ocupados,
                'disponibles': motos_total - motos_ocupados,
                'porcentaje': round((motos_ocupados / motos_total * 100) if motos_total > 0 else 0, 1)
            },
            'discapacitado': {
                'total': discapacitados_total,
                'ocupados': discapacitados_ocupados,
                'disponibles': discapacitados_total - discapacitados_ocupados,
                'porcentaje': round((discapacitados_ocupados / discapacitados_total * 100) if discapacitados_total > 0 else 0, 1)
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error al obtener ocupación por tipo: {e}")
        return jsonify({"error": str(e)}), 500



