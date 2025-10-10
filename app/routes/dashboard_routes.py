from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@jwt_required()
def dashboard():
    try:
        usuario_id = int(get_jwt_identity())
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return redirect(url_for('auth.index'))
        
        return render_template('dashboard.html', usuario=usuario, active_page='dashboard')
    except Exception as e:
        print(f"Error en dashboard: {e}")
        return redirect(url_for('auth.index'))


