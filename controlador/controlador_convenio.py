from typing import Tuple

from modelo.entidades import Convenio
from modelo.repositorio import Repositorio


class ControladorConvenio:
    def __init__(self): self.repo = Repositorio()

    def agregar(self, id_empresa: str, fi: str, ff: str) -> Tuple[bool, str]:
        if not self.repo.obtener_empresa(id_empresa):
            return False, "Empresa no existe."
        if fi > ff: return False, "La fecha de inicio no puede ser posterior a la fecha de fin."
        c = Convenio(fecha_inicio=fi, fecha_fin=ff, id_empresa=id_empresa)
        self.repo.agregar_convenio(c)
        return True, f"Convenio registrado (ID: {c.id_convenio})."

    def actualizar(self, id_: str, fi: str, ff: str) -> Tuple[bool, str]:
        c = self.repo.obtener_convenio(id_)
        if not c: return False, "Convenio no encontrado."
        if fi > ff: return False, "Fechas inválidas."
        c.fecha_inicio, c.fecha_fin = fi, ff
        self.repo.actualizar_convenio(c)
        return True, "Convenio actualizado."

    def eliminar(self, id_: str) -> Tuple[bool, str]:
        self.repo.eliminar_convenio(id_)
        return True, "Convenio eliminado."

    def listar(self):              return self.repo.listar_convenios()
    def de_empresa(self, id_):     return self.repo.convenios_empresa(id_)
    def tiene_vigente(self, id_empresa): return self.repo.tiene_convenio_vigente(id_empresa)
