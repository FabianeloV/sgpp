from dataclasses import dataclass, field

from .id_generator import gen_id


@dataclass
class Documento:
    id_practica: str
    tipo: str           # carta_compromiso, CV, malla, otro
    nombre_archivo: str
    fecha_subida: str
    id_documento: str = field(default_factory=gen_id)
