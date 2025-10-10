from datetime import datetime
from app.extensions import db

class Reporte(db.Model):
    __tablename__ = 'reportes'
    id = db.Column(db.Integer, primary_key=True)
    tipo_reporte = db.Column(db.String(100))  # diario, mensual, anual
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    contenido = db.Column(db.Text)  # JSON, CSV o texto
    descripcion = db.Column(db.String(255))

    def __repr__(self):
        return f'<Reporte {self.tipo_reporte} generado {self.fecha_generacion}>'
