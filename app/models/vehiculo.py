from app.extensions import db
from datetime import datetime, timezone

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    
    # Campos opcionales (se pueden llenar después)
    marca = db.Column(db.String(50), nullable=True)
    modelo = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(30), nullable=True)
    propietario = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    activo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Vehiculo {self.placa}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'placa': self.placa,
            'marca': self.marca,
            'modelo': self.modelo,
            'color': self.color,
            'propietario': self.propietario,
            'telefono': self.telefono,
            'activo': self.activo
        }