from dataclasses import dataclass, field
from typing import Optional

from .estado_practica import EstadoPractica
from .id_generator import gen_id


@dataclass
class Practica:
    fecha_inicio: str
    id_postulacion: str
    id_t_academico: str
    id_t_empresarial: str
    estado: str = EstadoPractica.ACTIVA
    fecha_fin: Optional[str] = None
    observaciones: str = ""
    id_practica: str = field(default_factory=gen_id)
