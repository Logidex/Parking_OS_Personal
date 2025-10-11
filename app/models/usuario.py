from app.extensions import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(80), unique=True, nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)  # ⭐ Este es el campo
    rol = db.Column(db.String(20), nullable=False, default='usuario')
    
    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'

