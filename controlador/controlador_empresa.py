from typing import Tuple

from modelo.entidades import Empresa
from modelo.repositorio import Repositorio


class ControladorEmpresa:
    def __init__(self): self.repo = Repositorio()

    def agregar(self, nombre: str, ruc: str) -> Tuple[bool, str]:
        nombre, ruc = nombre.strip(), ruc.strip()
        if not nombre: return False, "El nombre no puede estar vacío."
        if not ruc:    return False, "El RUC no puede estar vacío."
        e = Empresa(nombre=nombre, RUC=ruc)
        self.repo.agregar_empresa(e)
        return True, f"Empresa '{nombre}' registrada (ID: {e.id_empresa})."

    def actualizar(self, id_: str, nombre: str, ruc: str) -> Tuple[bool, str]:
        e = self.repo.obtener_empresa(id_)
        if not e: return False, "Empresa no encontrada."
        e.nombre, e.RUC = nombre.strip(), ruc.strip()
        self.repo.actualizar_empresa(e)
        return True, "Empresa actualizada."

    def eliminar(self, id_: str) -> Tuple[bool, str]:
        if self.repo.ofertas_empresa(id_):
            return False, "No se puede eliminar: la empresa tiene ofertas registradas."
        if self.repo.convenios_empresa(id_):
            return False, "No se puede eliminar: la empresa tiene convenios registrados."
        self.repo.eliminar_empresa(id_)
        return True, "Empresa eliminada."

    def listar(self):        return self.repo.listar_empresas()
    def obtener(self, id_):  return self.repo.obtener_empresa(id_)
    def contar_ofertas(self, id_): return len(self.repo.ofertas_empresa(id_))
