from flask import Flask, redirect, url_for
from werkzeug.security import generate_password_hash
from flask_jwt_extended import JWTManager
from app.extensions import db
from app.models.usuario import Usuario

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    
    db.init_app(app)
    jwt.init_app(app)

    # Importar y registrar blueprints
    from app.routes.auth_routes import login_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.vehiculos_routes import vehiculos_bp
    from app.routes.espacios_routes import espacios_bp
    from app.routes.tickets_routes import tickets_bp
    from app.routes.transacciones_routes import transacciones_bp
    from app.routes.reportes_routes import reportes_bp
    
    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vehiculos_bp)
    app.register_blueprint(espacios_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(transacciones_bp)
    app.register_blueprint(reportes_bp)
    
    @app.route('/')
    def index():
        #Redirige la raiz al login
        return redirect(url_for('/auth.index'))
    
    with app.app_context():
        db.create_all()

        if not Usuario.query.filter_by(nombre_usuario='admin').first():
            admin = Usuario(
                nombre_usuario='admin',
                password=generate_password_hash('SecretAdmin'),
                rol='admin',
                activo=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario admin creado correctamente")
    
    print("\n📋 Rutas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
    print()
            
    return app



