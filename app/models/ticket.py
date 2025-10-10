from app.extensions import db
from datetime import datetime, timezone

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'), nullable=False)
    espacio_id = db.Column(db.Integer, db.ForeignKey('espacios.id'), nullable=False)
    
    # Placa guardada por seguridad
    placa = db.Column(db.String(20), nullable=False)
    
    # Información del ticket
    # ⭐ FIX: Usar lambda con timezone.utc
    fecha_entrada = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    fecha_salida = db.Column(db.DateTime, nullable=True)
    
    # Estado del ticket
    estado = db.Column(db.String(20), default='activo')  # activo, finalizado
    
    # Cobro
    monto = db.Column(db.Float, default=0.0)
    
    # Información adicional
    tipo_vehiculo = db.Column(db.String(20))
    
    # Relaciones
    vehiculo = db.relationship('Vehiculo', backref='tickets', foreign_keys=[vehiculo_id])
    espacio = db.relationship('Espacio', backref='tickets', foreign_keys=[espacio_id])
    
    def __repr__(self):
        return f'<Ticket {self.id} - {self.placa} en {self.espacio.numero if self.espacio else "?"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'placa': self.placa,
            'vehiculo_id': self.vehiculo_id,
            'espacio_id': self.espacio_id,
            'espacio_numero': self.espacio.numero if self.espacio else None,
            'fecha_entrada': self.fecha_entrada.isoformat() if self.fecha_entrada else None,
            'fecha_salida': self.fecha_salida.isoformat() if self.fecha_salida else None,
            'estado': self.estado,
            'monto': self.monto,
            'tipo_vehiculo': self.tipo_vehiculo
        }


