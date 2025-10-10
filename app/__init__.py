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
        
        #Crear usuario admin su no existe
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
            
        # Crear espacios iniciales si no existen
        from app.models.espacio import Espacio
        
        if Espacio.query.count() == 0:
            print("Creando espacios iniciales...")
            espacios_iniciales = []
            
            # Seccion A - Espacios regulares (20 espacios)
            for i in range(1, 21):
                espacio = Espacio(
                    numero=f'A-{i:02d}', #A-01, A-02, ..., A-20
                    tipo='regular',
                    estado='disponible',
                    piso=1,
                    seccion='A'
                )
                espacios_iniciales.append(espacio)
                
            # Sección B - Espacios regulares (20 espacios)
            for i in range(1, 21):
                espacio = Espacio(
                    numero=f'B-{i:02d}',
                    tipo='regular',
                    estado='disponible',
                    piso=1,
                    seccion='B'
                )
                espacios_iniciales.append(espacio)
            
            # Sección C - Espacios para discapacitados (5 espacios)
            for i in range(1, 6):
                espacio = Espacio(
                    numero=f'C-{i:02d}',
                    tipo='discapacitado',
                    estado='disponible',
                    piso=1,
                    seccion='C'
                )
                espacios_iniciales.append(espacio)
            
            # Sección D - Espacios para motos (10 espacios)
            for i in range(1, 11):
                espacio = Espacio(
                    numero=f'D-{i:02d}',
                    tipo='moto',
                    estado='disponible',
                    piso=1,
                    seccion='D'
                )
                espacios_iniciales.append(espacio)
            
            # Agregar todos los espacios
            db.session.bulk_save_objects(espacios_iniciales)
            db.session.commit()
            print(f"✅ {len(espacios_iniciales)} espacios creados correctamente")
        else:
            print(f"ℹ️  Ya existen {Espacio.query.count()} espacios en la base de datos")
    
    print("\n📋 Rutas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
    print()
            
    return app



