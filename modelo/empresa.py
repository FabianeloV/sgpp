from dataclasses import dataclass, field

from .id_generator import gen_id


@dataclass
class Empresa:
    nombre: str
    RUC: str
    id_empresa: str = field(default_factory=gen_id)

    def __str__(self) -> str:
        return self.nombre
