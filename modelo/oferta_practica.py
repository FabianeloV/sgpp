from dataclasses import dataclass, field

from .estado_oferta import EstadoOferta
from .id_generator import gen_id


@dataclass
class OfertaPractica:
    descripcion: str
    requisitos: str
    id_empresa: str
    estado: str = EstadoOferta.ACTIVA
    id_oferta: str = field(default_factory=gen_id)
