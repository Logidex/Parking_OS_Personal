from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.extensions import db

vehiculos_bp = Blueprint('vehiculos', __name__)

@vehiculos_bp.route('/vehiculos')
@jwt_required()
def index():
    try:
        usuario_id = int(get_jwt_identity())
        usuario = db.session.get(Usuario, usuario_id)
        
        if not usuario:
            return redirect(url_for('/auth.index'))
        
        return render_template('vehiculos.html', usuario=usuario, active_page='vehiculos')
    except Exception as e:
        print(f"Error en vehículos: {e}")
        return redirect(url_for('/auth.index'))
