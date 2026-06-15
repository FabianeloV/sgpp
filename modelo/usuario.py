from dataclasses import dataclass, field
from typing import Optional

from .id_generator import gen_id


@dataclass
class Usuario:
    nombre: str                     # nombre de usuario para iniciar sesión
    password: str                   # texto plano (decisión del usuario)
    rol: str                        # uno de RolUsuario.TODOS
    ref_id: Optional[str] = None    # id de la entidad dueña según el rol
                                    # (id_empresa / id_estudiante / id_tutor / id_coordinador);
                                    # None para Administrador
    id_usuario: str = field(default_factory=gen_id)

    def __str__(self) -> str:
        return self.nombre
