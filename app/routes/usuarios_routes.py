from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from app.models.usuario import Usuario
from app.extensions import db

usuarios_bp = Blueprint('usuarios', __name__)


def es_admin():
    """Verifica si el usuario actual es administrador"""
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        return usuario and usuario.rol == 'admin'
    except:
        return False


@usuarios_bp.route('/usuarios')
@jwt_required()
def index():
    """Página principal de usuarios (solo admin)"""
    if not es_admin():
        return render_template('error.html', 
                             mensaje="No tienes permisos para acceder a esta página",
                             codigo=403), 403
    
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        
        return render_template('usuarios.html', usuario=usuario, active_page='usuarios')
    except Exception as e:
        print(f"Error en usuarios: {e}")
        return redirect(url_for('auth.index'))


# ===== API ENDPOINTS =====

@usuarios_bp.route('/api/usuarios', methods=['GET'])
@jwt_required()
def listar_usuarios():
    """Listar todos los usuarios (solo admin)"""
    if not es_admin():
        return jsonify({"error": "No tienes permisos"}), 403
    
    try:
        usuarios = Usuario.query.all()
        
        resultado = []
        for usuario in usuarios:
            resultado.append({
                'id': usuario.id,
                'nombre_usuario': usuario.nombre_usuario,
                'rol': usuario.rol
            })
        
        return jsonify(resultado), 200
        
    except Exception as e:
        print(f"❌ Error al listar usuarios: {e}")
        return jsonify({"error": str(e)}), 500


@usuarios_bp.route('/api/usuarios', methods=['POST'])
@jwt_required()
def crear_usuario():
    """Crear un nuevo usuario (solo admin)"""
    if not es_admin():
        return jsonify({"error": "No tienes permisos"}), 403
    
    try:
        data = request.get_json()
        
        nombre_usuario = data.get('nombre_usuario')
        password = data.get('password')
        rol = data.get('rol', 'usuario')
        
        # Validaciones
        if not nombre_usuario or not password:
            return jsonify({"error": "Nombre de usuario y contraseña son requeridos"}), 400
        
        # Verificar que el usuario no exista
        if Usuario.query.filter_by(nombre_usuario=nombre_usuario).first():
            return jsonify({"error": "El usuario ya existe"}), 400
        
        # Validar rol
        if rol not in ['admin', 'usuario']:
            return jsonify({"error": "Rol inválido"}), 400
        
        # Crear usuario
        nuevo_usuario = Usuario(
            nombre_usuario=nombre_usuario,
            contraseña=generate_password_hash(password),
            rol=rol
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({
            "mensaje": "Usuario creado exitosamente",
            "usuario": {
                'id': nuevo_usuario.id,
                'nombre_usuario': nuevo_usuario.nombre_usuario,
                'rol': nuevo_usuario.rol
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear usuario: {e}")
        return jsonify({"error": str(e)}), 500


@usuarios_bp.route('/api/usuarios/<int:usuario_id>', methods=['DELETE'])
@jwt_required()
def eliminar_usuario(usuario_id):
    """Eliminar un usuario (solo admin)"""
    if not es_admin():
        return jsonify({"error": "No tienes permisos"}), 403
    
    try:
        # No permitir eliminar al usuario actual
        usuario_actual_id = int(get_jwt_identity())
        if usuario_id == usuario_actual_id:
            return jsonify({"error": "No puedes eliminar tu propio usuario"}), 400
        
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # No permitir eliminar al último admin
        if usuario.rol == 'admin':
            total_admins = Usuario.query.filter_by(rol='admin').count()
            if total_admins <= 1:
                return jsonify({"error": "No puedes eliminar al último administrador"}), 400
        
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al eliminar usuario: {e}")
        return jsonify({"error": str(e)}), 500


@usuarios_bp.route('/api/usuarios/<int:usuario_id>/cambiar-password', methods=['PUT'])
@jwt_required()
def cambiar_password(usuario_id):
    """Cambiar contraseña de un usuario (solo admin o el mismo usuario)"""
    try:
        usuario_actual_id = int(get_jwt_identity())
        
        # Solo admin o el mismo usuario pueden cambiar la contraseña
        if not es_admin() and usuario_actual_id != usuario_id:
            return jsonify({"error": "No tienes permisos"}), 403
        
        data = request.get_json()
        nueva_password = data.get('nueva_password')
        
        if not nueva_password:
            return jsonify({"error": "La nueva contraseña es requerida"}), 400
        
        if len(nueva_password) < 4:
            return jsonify({"error": "La contraseña debe tener al menos 4 caracteres"}), 400
        
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        usuario.contraseña = generate_password_hash(nueva_password)
        db.session.commit()
        
        return jsonify({"mensaje": "Contraseña cambiada exitosamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al cambiar contraseña: {e}")
        return jsonify({"error": str(e)}), 500


@usuarios_bp.route('/api/usuarios/<int:usuario_id>/cambiar-rol', methods=['PUT'])
@jwt_required()
def cambiar_rol(usuario_id):
    """Cambiar rol de un usuario (solo admin)"""
    if not es_admin():
        return jsonify({"error": "No tienes permisos"}), 403
    
    try:
        # No permitir cambiar rol del usuario actual
        usuario_actual_id = int(get_jwt_identity())
        if usuario_id == usuario_actual_id:
            return jsonify({"error": "No puedes cambiar tu propio rol"}), 400
        
        data = request.get_json()
        nuevo_rol = data.get('rol')
        
        if nuevo_rol not in ['admin', 'usuario']:
            return jsonify({"error": "Rol inválido"}), 400
        
        usuario = Usuario.query.filter_by(id=usuario_id).first()
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # No permitir cambiar el rol si es el último admin
        if usuario.rol == 'admin' and nuevo_rol == 'usuario':
            total_admins = Usuario.query.filter_by(rol='admin').count()
            if total_admins <= 1:
                return jsonify({"error": "No puedes cambiar el rol del último administrador"}), 400
        
        usuario.rol = nuevo_rol
        db.session.commit()
        
        return jsonify({
            "mensaje": "Rol cambiado exitosamente",
            "usuario": {
                'id': usuario.id,
                'nombre_usuario': usuario.nombre_usuario,
                'rol': usuario.rol
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al cambiar rol: {e}")
        return jsonify({"error": str(e)}), 500

