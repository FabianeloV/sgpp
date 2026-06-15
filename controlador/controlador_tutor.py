from typing import Tuple

from modelo.entidades import TutorAcademico, TutorEmpresarial
from modelo.repositorio import Repositorio


class ControladorTutor:
    def __init__(self): self.repo = Repositorio()

    # Académico
    def agregar_academico(self, nombre: str, apellido: str, correo: str,
                           telefono: str, area: str) -> Tuple[bool, str]:
        if not nombre.strip(): return False, "Nombre requerido."
        t = TutorAcademico(nombre=nombre.strip(), apellido=apellido.strip(),
                            correo=correo.strip(), telefono=telefono.strip(), area=area.strip())
        self.repo.agregar_t_academico(t)
        return True, f"Tutor académico registrado (ID: {t.id_tutor})."

    def actualizar_academico(self, id_: str, nombre: str, apellido: str,
                               correo: str, telefono: str, area: str) -> Tuple[bool, str]:
        t = self.repo.obtener_t_academico(id_)
        if not t: return False, "Tutor no encontrado."
        t.nombre, t.apellido = nombre.strip(), apellido.strip()
        t.correo, t.telefono, t.area = correo.strip(), telefono.strip(), area.strip()
        self.repo.actualizar_t_academico(t)
        return True, "Tutor académico actualizado."

    def eliminar_academico(self, id_: str) -> Tuple[bool, str]:
        for p in self.repo.listar_practicas():
            if p.id_t_academico == id_:
                return False, "No se puede eliminar: tiene prácticas asignadas."
        self.repo.eliminar_t_academico(id_)
        return True, "Tutor académico eliminado."

    # Empresarial
    def agregar_empresarial(self, nombre: str, apellido: str, correo: str,
                             telefono: str, cargo: str, id_empresa: str = "") -> Tuple[bool, str]:
        if not nombre.strip(): return False, "Nombre requerido."
        t = TutorEmpresarial(nombre=nombre.strip(), apellido=apellido.strip(),
                              correo=correo.strip(), telefono=telefono.strip(),
                              cargo=cargo.strip(), id_empresa=id_empresa.strip())
        self.repo.agregar_t_empresarial(t)
        return True, f"Tutor empresarial registrado (ID: {t.id_tutor})."

    def actualizar_empresarial(self, id_: str, nombre: str, apellido: str,
                                correo: str, telefono: str, cargo: str,
                                id_empresa: str = "") -> Tuple[bool, str]:
        t = self.repo.obtener_t_empresarial(id_)
        if not t: return False, "Tutor no encontrado."
        t.nombre, t.apellido = nombre.strip(), apellido.strip()
        t.correo, t.telefono, t.cargo = correo.strip(), telefono.strip(), cargo.strip()
        if id_empresa.strip():   # preservar el vínculo si no se especifica uno nuevo
            t.id_empresa = id_empresa.strip()
        self.repo.actualizar_t_empresarial(t)
        return True, "Tutor empresarial actualizado."

    def eliminar_empresarial(self, id_: str) -> Tuple[bool, str]:
        for p in self.repo.listar_practicas():
            if p.id_t_empresarial == id_:
                return False, "No se puede eliminar: tiene prácticas asignadas."
        self.repo.eliminar_t_empresarial(id_)
        return True, "Tutor empresarial eliminado."

    def listar_academicos(self):    return self.repo.listar_t_academicos()
    def listar_empresariales(self): return self.repo.listar_t_empresariales()
    def obtener_academico(self, id_):    return self.repo.obtener_t_academico(id_)
    def obtener_empresarial(self, id_):  return self.repo.obtener_t_empresarial(id_)
