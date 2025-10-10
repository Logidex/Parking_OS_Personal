from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets')
@jwt_required()
def index():
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return redirect(url_for('auth.index'))
        
        return render_template('tickets.html', usuario=usuario, active_page='tickets')
    except Exception as e:
        print(f"Error en tickets: {e}")
        return redirect(url_for('auth.index'))
