from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, set_access_cookies, unset_jwt_cookies
from werkzeug.security import check_password_hash
from app.models.usuario import Usuario
from app.extensions import db

login_bp = Blueprint('/auth', __name__)

@login_bp.route('/')
def index():
    return render_template('login.html')

@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nombre_usuario = data.get('nombre_usuario')
    password = data.get('password')

    if not nombre_usuario or not password:
        return jsonify({"error": "Faltan datos"}), 400

    usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 401
    
    if not check_password_hash(usuario.password, password):
        return jsonify({"error": "Contraseña incorrecta"}), 401

    # IMPORTANTE: Convertir el ID a string
    access_token = create_access_token(identity=str(usuario.id))
    
    response = jsonify({
        "mensaje": "Login exitoso",
        "usuario": usuario.nombre_usuario,
        "rol": usuario.rol
    })
    
    # Guardar el token en una cookie HTTP-only
    set_access_cookies(response, access_token)
    
    return response, 200

@login_bp.route('/session-info', methods=['GET'])
@jwt_required()
def session_info():
    """Obtener información de la sesión actual"""
    from flask_jwt_extended import get_jwt
    from datetime import datetime, timezone
    
    try:
        jwt_data = get_jwt()
        
        # Obtener timestamp de expiración
        exp_timestamp = jwt_data.get('exp')
        
        if exp_timestamp:
            # Convertir timestamp a datetime
            expiration_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            
            # Calcular tiempo restante
            time_remaining = expiration_time - now
            
            # Convertir a minutos y horas
            total_seconds = int(time_remaining.total_seconds())
            
            if total_seconds < 0:
                # Token ya expiró
                return jsonify({
                    "expira_en": "Expirado",
                    "tiempo_restante_segundos": 0
                }), 401
            
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            
            return jsonify({
                "expira_en": f"{hours}h {minutes}m",
                "expiracion": expiration_time.isoformat(),
                "tiempo_restante_segundos": total_seconds,
                "horas": hours,
                "minutos": minutes
            }), 200
        else:
            return jsonify({"error": "No se pudo obtener información de expiración"}), 400
            
    except Exception as e:
        print(f"❌ Error en session-info: {e}")
        return jsonify({"error": str(e)}), 500


@login_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"mensaje": "Logout exitoso"})
    unset_jwt_cookies(response)
    return response, 200



    