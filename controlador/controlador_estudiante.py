from typing import Tuple

from modelo.entidades import Estudiante
from modelo.repositorio import Repositorio


class ControladorEstudiante:
    def __init__(self): self.repo = Repositorio()

    def agregar(self, nombre: str, apellido: str, correo: str, telefono: str,
                ciclo: int, malla: str, cv: str, previa: bool) -> Tuple[bool, str]:
        if not nombre.strip():  return False, "Nombre requerido."
        if not correo.strip():  return False, "Correo requerido."
        if ciclo < 1 or ciclo > 10: return False, "Ciclo debe estar entre 1 y 10."
        e = Estudiante(
            nombre=nombre.strip(), apellido=apellido.strip(),
            correo=correo.strip(), telefono=telefono.strip(),
            ciclo=ciclo, malla=malla.strip(), CV=cv.strip(),
            tiene_practica_previa=previa,
        )
        self.repo.agregar_estudiante(e)
        return True, f"Estudiante '{e.nombre_completo}' registrado (ID: {e.id_estudiante})."

    def actualizar(self, id_: str, nombre: str, apellido: str, correo: str,
                   telefono: str, ciclo: int, malla: str, cv: str, previa: bool) -> Tuple[bool, str]:
        e = self.repo.obtener_estudiante(id_)
        if not e: return False, "Estudiante no encontrado."
        e.nombre, e.apellido = nombre.strip(), apellido.strip()
        e.correo, e.telefono = correo.strip(), telefono.strip()
        e.ciclo, e.malla, e.CV = ciclo, malla.strip(), cv.strip()
        e.tiene_practica_previa = previa
        self.repo.actualizar_estudiante(e)
        return True, "Estudiante actualizado."

    def eliminar(self, id_: str) -> Tuple[bool, str]:
        if self.repo.postulaciones_estudiante(id_):
            return False, "No se puede eliminar: el estudiante tiene postulaciones."
        self.repo.eliminar_estudiante(id_)
        return True, "Estudiante eliminado."

    def listar(self):       return self.repo.listar_estudiantes()
    def obtener(self, id_): return self.repo.obtener_estudiante(id_)
