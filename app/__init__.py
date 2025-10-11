from flask import Flask, redirect, url_for
from werkzeug.security import generate_password_hash
from flask_jwt_extended import JWTManager
from app.extensions import db
from app.models.usuario import Usuario
from app.models.espacio import Espacio
import sys

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    
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
    
    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(vehiculos_bp)
    app.register_blueprint(espacios_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(transacciones_bp)
    app.register_blueprint(reportes_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.index'))
    
    # ⭐ DETECTAR SI ESTAMOS EN TESTING
    # Verificar si pytest está corriendo
    is_testing = 'pytest' in sys.modules or app.config.get('TESTING', False)
    
    # Solo crear datos iniciales si NO estamos en testing
    if not is_testing:
        with app.app_context():
            db.create_all()
            
            # Crear usuario admin si no existe
            if not Usuario.query.filter_by(nombre_usuario='admin').first():
                admin = Usuario(
                    nombre_usuario='admin',
                    contraseña=generate_password_hash('admin'),
                    rol='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuario admin creado correctamente")
            
            # Crear espacios iniciales si no existen
            if Espacio.query.count() == 0:
                print("Creando espacios iniciales...")
                espacios_iniciales = []
                
                # Espacios regulares (A y B)
                for seccion in ['A', 'B']:
                    for i in range(1, 21):
                        espacio = Espacio(
                            numero=f'{seccion}-{i:02d}',
                            tipo='regular',
                            estado='disponible',
                            piso=1,
                            seccion=seccion
                        )
                        espacios_iniciales.append(espacio)
                
                # Espacios para discapacitados (C)
                for i in range(1, 6):
                    espacio = Espacio(
                        numero=f'C-{i:02d}',
                        tipo='discapacitado',
                        estado='disponible',
                        piso=1,
                        seccion='C'
                    )
                    espacios_iniciales.append(espacio)
                
                # Espacios para motos (D)
                for i in range(1, 11):
                    espacio = Espacio(
                        numero=f'D-{i:02d}',
                        tipo='moto',
                        estado='disponible',
                        piso=1,
                        seccion='D'
                    )
                    espacios_iniciales.append(espacio)
                
                db.session.bulk_save_objects(espacios_iniciales)
                db.session.commit()
                print(f"✅ {len(espacios_iniciales)} espacios creados correctamente")
            
            # Imprimir rutas registradas
            print("\n📋 Rutas registradas:")
            for rule in app.url_map.iter_rules():
                if not rule.endpoint.startswith('static'):
                    print(f"  {rule.endpoint}: {rule.rule} {list(rule.methods - {'HEAD', 'OPTIONS'})}")
    
    return app






