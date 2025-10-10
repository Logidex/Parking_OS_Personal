# app/models/parqueo.py (o donde lo tengas)
from app.extensions import db

class Parqueo(db.Model):
    __tablename__ = 'parqueos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    capacidad = db.Column(db.Integer)
    activo = db.Column(db.Boolean, default=True)
    
    # ⭐ Ahora SÍ puede haber relación porque existe foreign key en Espacio
    espacios = db.relationship('Espacio', backref='parqueo', lazy=True)
    
    def __repr__(self):
        return f'<Parqueo {self.nombre}>'
