from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.extensions import db

transacciones_bp = Blueprint('transacciones', __name__)

@transacciones_bp.route('/transacciones')
@jwt_required()
def index():
    try:
        usuario_id = int(get_jwt_identity())
        usuario = db.session.get(Usuario, usuario_id) 
        
        if not usuario:
            return redirect(url_for('auth.index'))
        
        return render_template('transacciones.html', usuario=usuario, active_page='transacciones')
    except Exception as e:
        print(f"Error en transacciones: {e}")
        return redirect(url_for('auth.index'))
