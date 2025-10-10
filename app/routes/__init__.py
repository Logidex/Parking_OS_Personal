from .auth_routes import login_bp
from .dashboard_routes import dashboard_bp
from .vehiculos_routes import vehiculos_bp
from .espacios_routes import espacios_bp
from .tickets_routes import tickets_bp
from .transacciones_routes import transacciones_bp
from .reportes_routes import reportes_bp

blueprints = [
    login_bp,
    dashboard_bp,
    vehiculos_bp,
    espacios_bp,
    tickets_bp,
    transacciones_bp,
    reportes_bp
]

