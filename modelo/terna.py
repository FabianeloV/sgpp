from dataclasses import dataclass, field
from typing import List

from .estado_terna import EstadoTerna
from .id_generator import gen_id


@dataclass
class Terna:
    """Shortlist de hasta 3 postulaciones por oferta enviada a la empresa."""
    id_oferta: str
    id_postulaciones: List[str] = field(default_factory=list)
    estado: str = EstadoTerna.ACTIVA
    id_terna: str = field(default_factory=gen_id)

    MAX = 3

    def agregar(self, id_postulacion: str) -> bool:
        if len(self.id_postulaciones) >= self.MAX:
            return False
        if id_postulacion not in self.id_postulaciones:
            self.id_postulaciones.append(id_postulacion)
            return True
        return False

    def esta_completa(self) -> bool:
        return len(self.id_postulaciones) >= self.MAX

    def remover(self, id_postulacion: str):
        if id_postulacion in self.id_postulaciones:
            self.id_postulaciones.remove(id_postulacion)
