from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.espacio import Espacio
from app.models.usuario import Usuario
from app.models.vehiculo import Vehiculo
from app.extensions import db

vehiculos_bp = Blueprint('vehiculos', __name__)

@vehiculos_bp.route('/vehiculos')
@jwt_required()
def index():
    """Página principal de vehículos"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        
        if not usuario:
            return redirect(url_for('auth.index'))
        
        return render_template('vehiculos.html', usuario=usuario, active_page='vehiculos')
    except Exception as e:
        print(f"Error en vehículos: {e}")
        return redirect(url_for('auth.index'))


# ===== API ENDPOINTS =====

@vehiculos_bp.route('/api/vehiculos', methods=['GET'])
@jwt_required()
def listar_vehiculos():
    """Listar todos los vehículos (API)"""
    try:
        # Filtros opcionales
        tipo = request.args.get('tipo')
        buscar = request.args.get('buscar')  # Buscar por placa, marca o modelo
        
        query = Vehiculo.query.filter_by(activo=True)
        
        if tipo:
            query = query.filter_by(tipo=tipo)
        
        if buscar:
            # Buscar en placa, marca o modelo
            buscar = f"%{buscar}%"
            query = query.filter(
                db.or_(
                    Vehiculo.placa.ilike(buscar),
                    Vehiculo.marca.ilike(buscar),
                    Vehiculo.modelo.ilike(buscar)
                )
            )
        
        vehiculos = query.order_by(Vehiculo.fecha_registro.desc()).all()
        
        return jsonify([vehiculo.to_dict() for vehiculo in vehiculos]), 200
    except Exception as e:
        print(f"❌ Error al listar vehículos: {e}")
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route('/api/vehiculos', methods=['POST'])
@jwt_required()
def crear_vehiculo():
    """Crear un nuevo vehículo (solo registrarlo, no ingresarlo al parqueo)"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data or not data.get('placa'):
            return jsonify({"error": "La placa es requerida"}), 400
        
        # Normalizar placa (mayúsculas, sin espacios)
        placa = data['placa'].strip().upper()
        
        # Verificar que no exista duplicado
        if Vehiculo.query.filter_by(placa=placa).first():
            return jsonify({"error": f"Ya existe un vehículo con la placa {placa}"}), 409
        
        # Crear vehículo (todos los campos opcionales excepto placa)
        nuevo_vehiculo = Vehiculo(
            placa=placa,
            marca=data.get('marca', '').strip() if data.get('marca') else None,
            modelo=data.get('modelo', '').strip() if data.get('modelo') else None,
            color=data.get('color', '').strip() if data.get('color') else None,
            propietario=data.get('propietario', '').strip() if data.get('propietario') else None,
            telefono=data.get('telefono', '').strip() if data.get('telefono') else None
        )
        
        db.session.add(nuevo_vehiculo)
        db.session.commit()
        
        return jsonify({
            "mensaje": "Vehículo creado exitosamente",
            "vehiculo": nuevo_vehiculo.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear vehículo: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route('/api/vehiculos/<int:vehiculo_id>', methods=['GET'])
@jwt_required()
def obtener_vehiculo(vehiculo_id):
    """Obtener un vehículo específico"""
    try:
        vehiculo = Vehiculo.query.filter_by(id=vehiculo_id).first()
        
        if not vehiculo:
            return jsonify({"error": "Vehículo no encontrado"}), 404
        
        return jsonify(vehiculo.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route('/api/vehiculos/<int:vehiculo_id>', methods=['PUT'])
@jwt_required()
def actualizar_vehiculo(vehiculo_id):
    """Actualizar un vehículo"""
    try:
        vehiculo = Vehiculo.query.filter_by(id=vehiculo_id).first()
        
        if not vehiculo:
            return jsonify({"error": "Vehículo no encontrado"}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos (placa NO se puede cambiar)
        if 'marca' in data:
            vehiculo.marca = data['marca'].strip()
        if 'modelo' in data:
            vehiculo.modelo = data['modelo'].strip()
        if 'color' in data:
            vehiculo.color = data['color'].strip()
        if 'tipo' in data:
            vehiculo.tipo = data['tipo']
        if 'propietario' in data:
            vehiculo.propietario = data['propietario'].strip() if data['propietario'] else None
        if 'telefono' in data:
            vehiculo.telefono = data['telefono'].strip() if data['telefono'] else None
        
        db.session.commit()
        
        return jsonify({
            "mensaje": "Vehículo actualizado exitosamente",
            "vehiculo": vehiculo.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al actualizar vehículo: {e}")
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route('/api/vehiculos/<int:vehiculo_id>', methods=['DELETE'])
@jwt_required()
def eliminar_vehiculo(vehiculo_id):
    """Eliminar un vehículo (solo admin)"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        
        # Verificar que sea admin
        if not usuario or usuario.rol != 'admin':
            return jsonify({"error": "No tienes permisos para eliminar vehículos"}), 403
        
        vehiculo = Vehiculo.query.filter_by(id=vehiculo_id).first()
        
        if not vehiculo:
            return jsonify({"error": "Vehículo no encontrado"}), 404
        
        # Guardar placa para el mensaje
        placa = vehiculo.placa
        
        # Eliminar el vehículo
        db.session.delete(vehiculo)
        db.session.commit()
        
        return jsonify({
            "mensaje": f"Vehículo {placa} eliminado correctamente"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al eliminar vehículo: {e}")
        return jsonify({"error": str(e)}), 500


@vehiculos_bp.route('/api/vehiculos/estadisticas', methods=['GET'])
@jwt_required()
def estadisticas_vehiculos():
    """Obtener estadísticas de vehículos"""
    try:
        total = Vehiculo.query.filter_by(activo=True).count()
        
        # Contar por tipo
        tipos = db.session.query(
            Vehiculo.tipo,
            db.func.count(Vehiculo.id)
        ).filter_by(activo=True).group_by(Vehiculo.tipo).all()
        
        tipos_dict = {tipo: count for tipo, count in tipos}
        
        return jsonify({
            "total": total,
            "por_tipo": tipos_dict
        }), 200
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
        return jsonify({"error": str(e)}), 500

@vehiculos_bp.route('/api/espacios/disponibles-por-tipo', methods=['GET'])
@jwt_required()
def espacios_disponibles_por_tipo():
    """Obtener espacios disponibles por tipo de vehículo"""
    try:
        # Contar espacios disponibles por tipo
        regulares = Espacio.query.filter_by(tipo='regular', estado='disponible', activo=True).count()
        motos = Espacio.query.filter_by(tipo='moto', estado='disponible', activo=True).count()
        discapacitados = Espacio.query.filter_by(tipo='discapacitado', estado='disponible', activo=True).count()
        
        return jsonify({
            'regular': regulares,
            'moto': motos,
            'discapacitado': discapacitados,
            'total': regulares + motos + discapacitados
        }), 200
        
    except Exception as e:
        print(f"❌ Error al obtener espacios disponibles: {e}")
        return jsonify({"error": str(e)}), 500
