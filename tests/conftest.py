import pytest
from app import create_app, db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    """Creacion de instancia de la app para testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' #BD en memoria
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    
    with app.app_context():
        db.create_all()
        
        #Crear usuario de prueba
        usuario_test = Usuario(
            nombre_usuario='testuser',
            password=generate_password_hash('testpass'),
            rol='admin',
            activo=True
        )
        db.session.add(usuario_test)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()
        
@pytest.fixture
def client(app):
    #Cliente para peticiones http de prueba
    return app.test_client()

@pytest.fixture
def runner(app):
    #Runner para ejecutar comandos CLI
    return app.test_cli_runner()
    