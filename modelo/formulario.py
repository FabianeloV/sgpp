from dataclasses import dataclass, field

from .id_generator import gen_id
from .tipo_formulario import TipoFormulario


@dataclass
class Formulario:
    tipo: int       # TipoFormulario.F1 / F2 / F3
    fecha: str
    id_practica: str
    firmado: bool = False
    observaciones: str = ""
    id_formulario: str = field(default_factory=gen_id)

    @property
    def nombre(self) -> str:
        return TipoFormulario.NOMBRES.get(self.tipo, f"Formulario {self.tipo}")
