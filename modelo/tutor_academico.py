from dataclasses import dataclass

from .tutor import Tutor


@dataclass
class TutorAcademico(Tutor):
    area: str = ""

    @property
    def tipo(self) -> str:
        return "Académico"
