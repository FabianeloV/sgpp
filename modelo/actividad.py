from dataclasses import dataclass, field
from typing import Optional

from .id_generator import gen_id


@dataclass
class Actividad:
    id_practica: str
    descripcion: str
    fecha: str
    validada: bool = False
    id_tutor_valida: Optional[str] = None
    id_actividad: str = field(default_factory=gen_id)
