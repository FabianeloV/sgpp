from dataclasses import dataclass, field
from datetime import date

from .id_generator import gen_id


@dataclass
class Convenio:
    fecha_inicio: str   # ISO: "2026-01-01"
    fecha_fin: str
    id_empresa: str
    id_convenio: str = field(default_factory=gen_id)

    def esta_vigente(self) -> bool:
        hoy = date.today().isoformat()
        return self.fecha_inicio <= hoy <= self.fecha_fin

    @property
    def estado_str(self) -> str:
        return "Vigente" if self.esta_vigente() else "Vencido"
