from dataclasses import dataclass, field

from .id_generator import gen_id


@dataclass
class Estudiante:
    nombre: str
    apellido: str
    correo: str
    telefono: str
    ciclo: int
    malla: str      # path o descripción del archivo de malla
    CV: str         # path o descripción del CV
    tiene_practica_previa: bool = False
    id_estudiante: str = field(default_factory=gen_id)

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def __str__(self) -> str:
        return self.nombre_completo

    def puede_practicas_externas(self) -> bool:
        """Regla de negocio: solo desde sexto ciclo."""
        return self.ciclo >= 6
