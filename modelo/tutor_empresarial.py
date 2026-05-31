from dataclasses import dataclass

from .tutor import Tutor


@dataclass
class TutorEmpresarial(Tutor):
    cargo: str = ""

    @property
    def tipo(self) -> str:
        return "Empresarial"
