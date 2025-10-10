from app.extensions import db

class Espacio(db.Model):
    __tablename__ = 'espacios'
    id = db.Column(db.Integer, primary_key=True)
    parqueo_id = db.Column(db.Integer, db.ForeignKey('parqueos.id'), nullable=False)
    tipo = db.Column(db.String(50))
    estado = db.Column(db.String(50), default='disponible')
    codigo = db.Column(db.String(20), nullable=False, unique=True)

    ticket = db.relationship('Ticket', backref='espacio', uselist=False)

    def __repr__(self):
        return f'<Espacio {self.codigo} estado {self.estado}>'
