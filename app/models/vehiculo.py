from app.extensions import db
from datetime import datetime, timezone

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(30), nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='sedan')  # sedan, suv, pickup, moto, etc.
    propietario = db.Column(db.String(100))  # Opcional
    telefono = db.Column(db.String(20))  # Opcional
    fecha_registro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    activo = db.Column(db.Boolean, default=True)
    
    # Relación con tickets (un vehículo puede tener muchos tickets)
    # tickets = db.relationship('Ticket', backref='vehiculo', lazy=True)
    
    def __repr__(self):
        return f'<Vehiculo {self.placa} - {self.marca} {self.modelo}>'
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'placa': self.placa,
            'marca': self.marca,
            'modelo': self.modelo,
            'color': self.color,
            'tipo': self.tipo,
            'propietario': self.propietario,
            'telefono': self.telefono,
            'activo': self.activo
        }

