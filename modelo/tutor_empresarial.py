from dataclasses import dataclass

from .tutor import Tutor


@dataclass
class TutorEmpresarial(Tutor):
    cargo: str = ""
    id_empresa: str = ""   # empresa dueña del tutor empresarial (vacío = sin asignar)

    @property
    def tipo(self) -> str:
        return "Empresarial"
