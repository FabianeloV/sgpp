from dataclasses import dataclass, field

from .id_generator import gen_id


@dataclass
class Tutor:
    """Superclase abstracta para tutores."""
    nombre: str
    apellido: str
    correo: str
    telefono: str
    id_tutor: str = field(default_factory=gen_id)

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def __str__(self) -> str:
        return self.nombre_completo
