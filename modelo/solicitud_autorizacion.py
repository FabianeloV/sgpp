from dataclasses import dataclass, field
from typing import Optional

from .estado_solicitud import EstadoSolicitud
from .id_generator import gen_id


@dataclass
class SolicitudAutorizacion:
    id_estudiante: str
    tipo: str           # TipoSolicitud
    fecha: str
    estado: str = EstadoSolicitud.PENDIENTE
    id_coordinador: Optional[str] = None
    id_empresa: Optional[str] = None
    observaciones: str = ""
    id_solicitud: str = field(default_factory=gen_id)
