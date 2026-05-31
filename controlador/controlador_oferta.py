from typing import Tuple

from modelo.entidades import OfertaPractica
from modelo.repositorio import Repositorio


class ControladorOferta:
    def __init__(self): self.repo = Repositorio()

    def agregar(self, id_empresa: str, desc: str, req: str) -> Tuple[bool, str]:
        if not self.repo.obtener_empresa(id_empresa):
            return False, "Empresa no existe."
        if not desc.strip(): return False, "La descripción es obligatoria."
        o = OfertaPractica(descripcion=desc.strip(), requisitos=req.strip(), id_empresa=id_empresa)
        self.repo.agregar_oferta(o)
        return True, f"Oferta registrada (ID: {o.id_oferta})."

    def actualizar(self, id_: str, id_empresa: str, desc: str, req: str, estado: str) -> Tuple[bool, str]:
        o = self.repo.obtener_oferta(id_)
        if not o: return False, "Oferta no encontrada."
        o.id_empresa, o.descripcion = id_empresa, desc.strip()
        o.requisitos, o.estado = req.strip(), estado
        self.repo.actualizar_oferta(o)
        return True, "Oferta actualizada."

    def eliminar(self, id_: str) -> Tuple[bool, str]:
        if self.repo.postulaciones_oferta(id_):
            return False, "No se puede eliminar: la oferta tiene postulaciones."
        self.repo.eliminar_oferta(id_)
        return True, "Oferta eliminada."

    def cambiar_estado(self, id_: str, estado: str) -> Tuple[bool, str]:
        o = self.repo.obtener_oferta(id_)
        if not o: return False, "Oferta no encontrada."
        o.estado = estado
        self.repo.actualizar_oferta(o)
        return True, f"Estado cambiado a '{estado}'."

    def listar(self):           return self.repo.listar_ofertas()
    def obtener(self, id_):     return self.repo.obtener_oferta(id_)
    def de_empresa(self, id_):  return self.repo.ofertas_empresa(id_)
    def contar_postulaciones(self, id_): return len(self.repo.postulaciones_oferta(id_))
    def estados(self): return EstadoOferta.TODOS
    def estado_activa(self): return EstadoOferta.ACTIVA
    def estado_cerrada(self): return EstadoOferta.CERRADA
