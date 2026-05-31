from typing import Tuple

from modelo.entidades import Coordinador
from modelo.repositorio import Repositorio


class ControladorCoordinador:
    def __init__(self): self.repo = Repositorio()

    def agregar(self, nombre: str, apellido: str, correo: str,
                telefono: str, cedula: str) -> Tuple[bool, str]:
        if not nombre.strip(): return False, "Nombre requerido."
        if not cedula.strip(): return False, "Cédula requerida."
        c = Coordinador(nombre=nombre.strip(), apellido=apellido.strip(),
                        correo=correo.strip(), telefono=telefono.strip(),
                        cedula=cedula.strip())
        self.repo.agregar_coordinador(c)
        return True, f"Coordinador registrado (ID: {c.id_coordinador})."

    def actualizar(self, id_: str, nombre: str, apellido: str,
                   correo: str, telefono: str, cedula: str) -> Tuple[bool, str]:
        c = self.repo.obtener_coordinador(id_)
        if not c: return False, "Coordinador no encontrado."
        c.nombre, c.apellido = nombre.strip(), apellido.strip()
        c.correo, c.telefono, c.cedula = correo.strip(), telefono.strip(), cedula.strip()
        self.repo.actualizar_coordinador(c)
        return True, "Coordinador actualizado."

    def eliminar(self, id_: str) -> Tuple[bool, str]:
        self.repo.eliminar_coordinador(id_)
        return True, "Coordinador eliminado."

    def listar(self):       return self.repo.listar_coordinadores()
    def obtener(self, id_): return self.repo.obtener_coordinador(id_)
