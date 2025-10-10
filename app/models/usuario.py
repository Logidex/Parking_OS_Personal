from app.extensions import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)  # almacena hash, ¡no texto plano!
    rol = db.Column(db.String(50), nullable=False)  # admin, operador, etc.
    fecha_creacion = db.Column(db.DateTime)
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'
