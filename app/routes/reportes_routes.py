from flask import Blueprint, redirect, render_template, jsonify, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.models.ticket import Ticket
from app.models.espacio import Espacio
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, desc
from app.extensions import db

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('/reportes')
@jwt_required()
def index():
    """Página principal de reportes"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        
        if not usuario:
            return redirect(url_for('auth.index'))
        
        return render_template('reportes.html', usuario=usuario, active_page='reportes')
    except Exception as e:
        print(f"Error en reportes: {e}")
        return redirect(url_for('auth.index'))


# ===== API ENDPOINTS =====

@reportes_bp.route('/api/reportes/ingresos-periodo', methods=['GET'])
@jwt_required()
def reporte_ingresos_periodo():
    """Generar reporte de ingresos por período"""
    try:
        # Ingresos de hoy
        hoy_inicio = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        tickets_hoy = Ticket.query.filter(
            Ticket.estado == 'finalizado',
            Ticket.fecha_salida >= hoy_inicio
        ).all()
        
        ingresos_hoy = sum(t.monto for t in tickets_hoy if t.monto)
        transacciones_hoy = len(tickets_hoy)
        
        # Ingresos de esta semana
        semana_inicio = hoy_inicio - timedelta(days=hoy_inicio.weekday())
        
        tickets_semana = Ticket.query.filter(
            Ticket.estado == 'finalizado',
            Ticket.fecha_salida >= semana_inicio
        ).all()
        
        ingresos_semana = sum(t.monto for t in tickets_semana if t.monto)
        transacciones_semana = len(tickets_semana)
        
        # Ingresos del mes
        mes_inicio = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        tickets_mes = Ticket.query.filter(
            Ticket.estado == 'finalizado',
            Ticket.fecha_salida >= mes_inicio
        ).all()
        
        ingresos_mes = sum(t.monto for t in tickets_mes if t.monto)
        transacciones_mes = len(tickets_mes)
        
        # Promedio por transacción
        promedio_hoy = (ingresos_hoy / transacciones_hoy) if transacciones_hoy > 0 else 0
        promedio_semana = (ingresos_semana / transacciones_semana) if transacciones_semana > 0 else 0
        promedio_mes = (ingresos_mes / transacciones_mes) if transacciones_mes > 0 else 0
        
        return jsonify({
            'hoy': {
                'ingresos': ingresos_hoy,
                'ingresos_formateado': f"RD${ingresos_hoy:,.2f}",
                'transacciones': transacciones_hoy,
                'promedio': promedio_hoy,
                'promedio_formateado': f"RD${promedio_hoy:,.2f}"
            },
            'semana': {
                'ingresos': ingresos_semana,
                'ingresos_formateado': f"RD${ingresos_semana:,.2f}",
                'transacciones': transacciones_semana,
                'promedio': promedio_semana,
                'promedio_formateado': f"RD${promedio_semana:,.2f}"
            },
            'mes': {
                'ingresos': ingresos_mes,
                'ingresos_formateado': f"RD${ingresos_mes:,.2f}",
                'transacciones': transacciones_mes,
                'promedio': promedio_mes,
                'promedio_formateado': f"RD${promedio_mes:,.2f}"
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error al generar reporte de ingresos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@reportes_bp.route('/api/reportes/ocupacion-espacios', methods=['GET'])
@jwt_required()
def reporte_ocupacion_espacios():
    """Generar reporte de ocupación de espacios"""
    try:
        # Total de tickets finalizados
        total_tickets = Ticket.query.filter_by(estado='finalizado').count()
        
        # Tickets por tipo de vehículo
        tickets_regular = Ticket.query.filter_by(estado='finalizado', tipo_vehiculo='regular').count()
        tickets_moto = Ticket.query.filter_by(estado='finalizado', tipo_vehiculo='moto').count()
        tickets_discapacitado = Ticket.query.filter_by(estado='finalizado', tipo_vehiculo='discapacitado').count()
        
        # Porcentajes
        porcentaje_regular = (tickets_regular / total_tickets * 100) if total_tickets > 0 else 0
        porcentaje_moto = (tickets_moto / total_tickets * 100) if total_tickets > 0 else 0
        porcentaje_discapacitado = (tickets_discapacitado / total_tickets * 100) if total_tickets > 0 else 0
        
        # Espacios disponibles vs ocupados (actual)
        espacios_total = Espacio.query.filter_by(activo=True).count()
        espacios_ocupados = Espacio.query.filter_by(estado='ocupado', activo=True).count()
        espacios_disponibles = espacios_total - espacios_ocupados
        
        # Tiempo promedio de estancia
        tickets_finalizados = Ticket.query.filter_by(estado='finalizado').all()
        tiempos = []
        
        for ticket in tickets_finalizados:
            if ticket.fecha_entrada and ticket.fecha_salida:
                fecha_entrada = ticket.fecha_entrada
                fecha_salida = ticket.fecha_salida
                
                if fecha_entrada.tzinfo is None:
                    fecha_entrada = fecha_entrada.replace(tzinfo=timezone.utc)
                if fecha_salida.tzinfo is None:
                    fecha_salida = fecha_salida.replace(tzinfo=timezone.utc)
                
                tiempo = fecha_salida - fecha_entrada
                tiempos.append(tiempo.total_seconds() / 3600)  # en horas
        
        tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
        
        return jsonify({
            'uso_por_tipo': {
                'regular': {
                    'cantidad': tickets_regular,
                    'porcentaje': round(porcentaje_regular, 1)
                },
                'moto': {
                    'cantidad': tickets_moto,
                    'porcentaje': round(porcentaje_moto, 1)
                },
                'discapacitado': {
                    'cantidad': tickets_discapacitado,
                    'porcentaje': round(porcentaje_discapacitado, 1)
                }
            },
            'ocupacion_actual': {
                'total': espacios_total,
                'ocupados': espacios_ocupados,
                'disponibles': espacios_disponibles,
                'porcentaje_ocupacion': round((espacios_ocupados / espacios_total * 100) if espacios_total > 0 else 0, 1)
            },
            'tiempo_promedio_estancia': round(tiempo_promedio, 2),
            'total_usos_historico': total_tickets
        }), 200
        
    except Exception as e:
        print(f"❌ Error al generar reporte de ocupación: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@reportes_bp.route('/api/reportes/vehiculos-frecuentes', methods=['GET'])
@jwt_required()
def reporte_vehiculos_frecuentes():
    """Generar reporte de vehículos frecuentes"""
    try:
        # Obtener vehículos con más visitas
        from sqlalchemy import func, desc
        
        vehiculos_frecuentes = db.session.query(
            Vehiculo.placa,
            Vehiculo.marca,
            Vehiculo.modelo,
            func.count(Ticket.id).label('visitas'),
            func.sum(Ticket.monto).label('total_gastado')
        ).join(
            Ticket, Vehiculo.id == Ticket.vehiculo_id
        ).filter(
            Ticket.estado == 'finalizado'
        ).group_by(
            Vehiculo.id
        ).order_by(
            desc('visitas')
        ).limit(10).all()
        
        resultado = []
        for vehiculo in vehiculos_frecuentes:
            resultado.append({
                'placa': vehiculo.placa,
                'marca': vehiculo.marca or 'N/A',
                'modelo': vehiculo.modelo or 'N/A',
                'visitas': vehiculo.visitas,
                'total_gastado': vehiculo.total_gastado or 0,
                'total_gastado_formateado': f"RD${vehiculo.total_gastado:,.2f}" if vehiculo.total_gastado else "RD$0.00"
            })
        
        return jsonify(resultado), 200
        
    except Exception as e:
        print(f"❌ Error al generar reporte de vehículos frecuentes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@reportes_bp.route('/api/reportes/metodos-pago', methods=['GET'])
@jwt_required()
def reporte_metodos_pago():
    """Generar reporte de métodos de pago"""
    try:
        tickets_finalizados = Ticket.query.filter_by(estado='finalizado').all()
        
        total_efectivo = sum(t.monto for t in tickets_finalizados if t.metodo_pago == 'efectivo' and t.monto)
        total_tarjeta = sum(t.monto for t in tickets_finalizados if t.metodo_pago == 'tarjeta' and t.monto)
        
        transacciones_efectivo = sum(1 for t in tickets_finalizados if t.metodo_pago == 'efectivo')
        transacciones_tarjeta = sum(1 for t in tickets_finalizados if t.metodo_pago == 'tarjeta')
        
        total_transacciones = transacciones_efectivo + transacciones_tarjeta
        
        return jsonify({
            'efectivo': {
                'monto': total_efectivo,
                'monto_formateado': f"RD${total_efectivo:,.2f}",
                'transacciones': transacciones_efectivo,
                'porcentaje': round((transacciones_efectivo / total_transacciones * 100) if total_transacciones > 0 else 0, 1)
            },
            'tarjeta': {
                'monto': total_tarjeta,
                'monto_formateado': f"RD${total_tarjeta:,.2f}",
                'transacciones': transacciones_tarjeta,
                'porcentaje': round((transacciones_tarjeta / total_transacciones * 100) if total_transacciones > 0 else 0, 1)
            },
            'total': {
                'monto': total_efectivo + total_tarjeta,
                'monto_formateado': f"RD${(total_efectivo + total_tarjeta):,.2f}",
                'transacciones': total_transacciones
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Error al generar reporte de métodos de pago: {e}")
        return jsonify({"error": str(e)}), 500

