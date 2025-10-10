from app.extensions import db
from datetime import datetime

class Espacio(db.Model):
    __tablename__ = 'espacios'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)  # Ej: "A-01"
    tipo = db.Column(db.String(20), nullable=False, default='regular')  # regular, discapacitado, moto
    estado = db.Column(db.String(20), nullable=False, default='disponible')  # disponible, ocupado, mantenimiento
    piso = db.Column(db.Integer, default=1)  # Para estacionamientos con varios pisos
    seccion = db.Column(db.String(5), default='A')  # A, B, C, etc.
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relación con tickets (un espacio puede tener muchos tickets)
    # tickets = db.relationship('Ticket', backref='espacio', lazy=True)
    
    def __repr__(self):
        return f'<Espacio {self.numero} - {self.estado}>'
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'id': self.id,
            'numero': self.numero,
            'tipo': self.tipo,
            'estado': self.estado,
            'piso': self.piso,
            'seccion': self.seccion,
            'activo': self.activo
        }

