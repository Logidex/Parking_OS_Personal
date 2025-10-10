from datetime import datetime
from app.extensions import db

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    hora_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    hora_salida = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.String(50), default='activo')
    
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'), nullable=False)
    espacio_id = db.Column(db.Integer, db.ForeignKey('espacios.id'), nullable=False)
    
    def calcular_tiempo_estancia(self):
        if self.hora_salida:
            delta = self.hora_salida - self.hora_entrada
        else:
            delta = datetime.utcnow() - self.hora_entrada
        return delta.total_seconds() / 60  # tiempo en minutos

    def __repr__(self):
        return f'<Ticket {self.id} estado {self.estado}>'
