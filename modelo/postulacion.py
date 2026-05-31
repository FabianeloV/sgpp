from dataclasses import dataclass, field
from typing import Optional

from .estado_postulacion import EstadoPostulacion
from .id_generator import gen_id


@dataclass
class Postulacion:
    fecha: str
    id_estudiante: str
    id_oferta: str
    estado: str = EstadoPostulacion.PENDIENTE
    id_coordinador: Optional[str] = None
    observaciones: str = ""
    id_postulacion: str = field(default_factory=gen_id)
