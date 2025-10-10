from .parqueo import Parqueo
from .espacio import Espacio
from .vehiculo import Vehiculo
from .ticket import Ticket
from .transaccion import Transaccion
from .historial import Historial
from .reporte import Reporte
from .usuario import Usuario

#Lista para importar en create_app()
models = [
    Parqueo,
    Espacio,
    Vehiculo,
    Ticket,
    Transaccion,
    Historial,
    Reporte,
    Usuario,
]