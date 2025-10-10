from datetime import datetime
from app.extensions import db

class Historial(db.Model):
    __tablename__ = 'historial'
    id = db.Column(db.Integer, primary_key=True)
    tipo_registro = db.Column(db.String(50))  # ticket o transaccion
    datos = db.Column(db.JSON)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Historial {self.tipo_registro} - {self.fecha}>'
