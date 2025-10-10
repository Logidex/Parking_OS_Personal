from app.extensions import db

class Parqueo(db.Model):
    __tablename__ = 'parqueos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(200))
    capacidad = db.Column(db.Integer)
    espacios = db.relationship('Espacio', backref='parqueo', lazy=True)
    
    def __repr__(self):
        return f'<Parqueo {self.nombre}>'