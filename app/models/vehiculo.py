from app.extensions import db

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(20), unique=True, nullable=False)
    tickets = db.relationship('Ticket', backref='vehiculo', lazy=True)

    def __repr__(self):
        return f'<Vehiculo {self.placa}>'
