from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.models.espacio import Espacio
from app.extensions import db

espacios_bp = Blueprint('espacios', __name__)

@espacios_bp.route('/espacios')
@jwt_required()
def index():
    try:
        usuario_id = int(get_jwt_identity())
        usuario = db.session.get(Usuario, usuario_id) 
        
        if not usuario:
            return redirect(url_for('auth.index'))
        
        return render_template('espacios.html', usuario=usuario, active_page='espacios')
    except Exception as e:
        print(f"Error en espacios: {e}")
        return redirect(url_for('auth.index'))
    

# ===== API ENDPOINTS =====

@espacios_bp.route('/api/espacios', methods=['GET'])
@jwt_required()
def listar_espacios():
    # Listar todos los espacios (API)
    try:
        # Filtros opcionales
        estado = request.args.get('estado') # disponible, ocupado, mantenimiento
        tipo = request.args.get('tipo') # regular, discapacitado, moto
        seccion = request.args.get('seccion') # A, B, C, D
        
        query = Espacio.query.filter_by(activo=True)
        
        if estado:
            query = query.filter_by(estado=estado)
        if tipo:
            query = query.filter_by(tipo=tipo)
        if seccion:
            query = query.filter_by(seccion=seccion)
            
        espacios = query.order_by(Espacio.numero).all()
        
        return jsonify([espacio.to_dict() for espacio in espacios]), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 500
    
@espacios_bp.route('/api/espacios', methods=['POST'])
@jwt_required()
def crear_espacio():
    """Crear un nuevo espacio (solo admin)"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        # Verificar que sea admin
        if usuario.rol != 'admin':
            return jsonify({"error": "No tienes permisos para crear espacios"}), 403
        
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('numero'):
            return jsonify({"error": "El número de espacio es requerido"}), 400
        
        # Verificar que no exista duplicado
        if Espacio.query.filter_by(numero=data['numero']).first():
            return jsonify({"error": f"El espacio {data['numero']} ya existe"}), 409
        
        # Crear espacio
        nuevo_espacio = Espacio(
            numero=data['numero'],
            tipo=data.get('tipo', 'regular'),
            estado=data.get('estado', 'disponible'),
            piso=data.get('piso', 1),
            seccion=data.get('seccion', data['numero'][0])  # Primera letra del número
        )
        
        db.session.add(nuevo_espacio)
        db.session.commit()
        
        return jsonify({
            "mensaje": "Espacio creado exitosamente",
            "espacio": nuevo_espacio.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@espacios_bp.route('/api/espacios/<int:espacio_id>', methods=['GET'])
@jwt_required()
def obtener_espacio(espacio_id):
    """Obtener un espacio específico"""
    try:
        espacio = Espacio.query.get(espacio_id)
        
        if not espacio:
            return jsonify({"error": "Espacio no encontrado"}), 404
        
        return jsonify(espacio.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@espacios_bp.route('/api/espacios/<int:espacio_id>', methods=['PUT'])
@jwt_required()
def actualizar_espacio(espacio_id):
    """Actualizar un espacio (solo admin)"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if usuario.rol != 'admin':
            return jsonify({"error": "No tienes permisos"}), 403
        
        espacio = Espacio.query.get(espacio_id)
        
        if not espacio:
            return jsonify({"error": "Espacio no encontrado"}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'tipo' in data:
            espacio.tipo = data['tipo']
        if 'estado' in data:
            espacio.estado = data['estado']
        if 'piso' in data:
            espacio.piso = data['piso']
        
        db.session.commit()
        
        return jsonify({
            "mensaje": "Espacio actualizado exitosamente",
            "espacio": espacio.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@espacios_bp.route('/api/espacios/<int:espacio_id>/cambiar-estado', methods=['PATCH'])
@jwt_required()
def cambiar_estado_espacio(espacio_id):
    """Cambiar estado de un espacio (disponible/ocupado/mantenimiento)"""
    try:
        espacio = Espacio.query.get(espacio_id)
        
        if not espacio:
            return jsonify({"error": "Espacio no encontrado"}), 404
        
        data = request.get_json()
        nuevo_estado = data.get('estado')
        
        if nuevo_estado not in ['disponible', 'ocupado', 'mantenimiento']:
            return jsonify({"error": "Estado inválido"}), 400
        
        espacio.estado = nuevo_estado
        db.session.commit()
        
        return jsonify({
            "mensaje": f"Estado cambiado a {nuevo_estado}",
            "espacio": espacio.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@espacios_bp.route('/api/espacios/estadisticas', methods=['GET'])
@jwt_required()
def estadisticas_espacios():
    """Obtener estadísticas de espacios"""
    try:
        total = Espacio.query.filter_by(activo=True).count()
        disponibles = Espacio.query.filter_by(estado='disponible', activo=True).count()
        ocupados = Espacio.query.filter_by(estado='ocupado', activo=True).count()
        mantenimiento = Espacio.query.filter_by(estado='mantenimiento', activo=True).count()
        
        return jsonify({
            "total": total,
            "disponibles": disponibles,
            "ocupados": ocupados,
            "mantenimiento": mantenimiento,
            "porcentaje_ocupacion": round((ocupados / total * 100) if total > 0 else 0, 2)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        