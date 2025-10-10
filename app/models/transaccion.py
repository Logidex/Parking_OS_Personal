from datetime import datetime
from app.extensions import db

class Transaccion(db.Model):
    __tablename__ = 'transacciones'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    monto_total = db.Column(db.Numeric(10, 2))
    metodo_pago = db.Column(db.String(50))
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(50), default='completado')

    def __repr__(self):
        return f'<Transaccion {self.id} - Monto: {self.monto_total}>'
