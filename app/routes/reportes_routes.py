from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes')
@jwt_required()
def index():
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return redirect(url_for('auth.index'))
        
        return render_template('reportes.html', usuario=usuario, active_page='reportes')
    except Exception as e:
        print(f"Error en reportes: {e}")
        return redirect(url_for('auth.index'))
