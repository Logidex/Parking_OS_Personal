from flask import Flask
from flask_jwt_extended import JWTManager
from app.extensions import db, jwt
import config

def create_app():
    app = Flask(__name__)
    
    # Cargar configuración desde config.py
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY
    app.config['JWT_TOKEN_LOCATION'] = config.JWT_TOKEN_LOCATION
    app.config['JWT_COOKIE_SECURE'] = config.JWT_COOKIE_SECURE
    app.config['JWT_COOKIE_CSRF_PROTECT'] = config.JWT_COOKIE_CSRF_PROTECT
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
    
    # Inicializar extensiones
    db.init_app(app)
    jwt.init_app(app)
    
    # Registrar blueprints
    from app.routes.auth_routes import login_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.vehiculos_routes import vehiculos_bp
    from app.routes.espacios_routes import espacios_bp
    from app.routes.tickets_routes import tickets_bp
    from app.routes.transacciones_routes import transacciones_bp
    from app.routes.reportes_routes import reportes_bp
    from app.routes.usuarios_routes import usuarios_bp
    
    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vehiculos_bp)
    app.register_blueprint(espacios_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(transacciones_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(usuarios_bp)
    
    # Crear tablas
    with app.app_context():
        db.create_all()
        
        # Crear usuario admin si no existe
        from app.models.usuario import Usuario
        from werkzeug.security import generate_password_hash
        
        admin = Usuario.query.filter_by(nombre_usuario='admin').first()
        if not admin:
            admin = Usuario(
                nombre_usuario='admin',
                contraseña=generate_password_hash('admin'),
                rol='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario admin creado")
    
    return app







