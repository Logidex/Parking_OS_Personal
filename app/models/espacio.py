# app/models/espacio.py
from app.extensions import db
from datetime import datetime, timezone

class Espacio(db.Model):
    __tablename__ = 'espacios'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False, default='regular')
    estado = db.Column(db.String(20), nullable=False, default='disponible')
    piso = db.Column(db.Integer, default=1)
    seccion = db.Column(db.String(5), default='A')
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    activo = db.Column(db.Boolean, default=True)
    parqueo_id = db.Column(db.Integer, db.ForeignKey('parqueos.id'), nullable=True)
    # nullable=True si un espacio puede NO pertenecer a un parqueo
    # nullable=False si SIEMPRE debe pertenecer a uno
    
    def __repr__(self):
        return f'<Espacio {self.numero} - {self.estado}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'tipo': self.tipo,
            'estado': self.estado,
            'piso': self.piso,
            'seccion': self.seccion,
            'activo': self.activo,
            'parqueo_id': self.parqueo_id
        }


