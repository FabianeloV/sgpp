from typing import Tuple

from modelo.entidades import EstadoPostulacion, EstadoTerna
from modelo.repositorio import Repositorio


class ControladorTerna:
    def __init__(self): self.repo = Repositorio()

    def enviar_a_empresa(self, id_: str) -> Tuple[bool, str]:
        t = self.repo.obtener_terna(id_)
        if not t: return False, "Terna no encontrada."
        if not t.id_postulaciones:
            return False, "La terna está vacía."
        t.estado = EstadoTerna.ENVIADA
        self.repo.actualizar_terna(t)
        return True, "Terna enviada a la empresa."

    def remover_postulacion(self, id_terna: str, id_postulacion: str) -> Tuple[bool, str]:
        t = self.repo.obtener_terna(id_terna)
        if not t: return False, "Terna no encontrada."
        t.remover(id_postulacion)
        p = self.repo.obtener_postulacion(id_postulacion)
        if p:
            p.estado = EstadoPostulacion.VALIDADA
            self.repo.actualizar_postulacion(p)
        self.repo.actualizar_terna(t)
        return True, "Postulación removida de la terna."

    def eliminar(self, id_: str) -> Tuple[bool, str]:
        t = self.repo.obtener_terna(id_)
        if not t: return False, "Terna no encontrada."
        for id_postulacion in t.id_postulaciones:
            p = self.repo.obtener_postulacion(id_postulacion)
            if p:
                p.estado = EstadoPostulacion.VALIDADA
                self.repo.actualizar_postulacion(p)
        self.repo.eliminar_terna(id_)
        return True, "Terna eliminada."

    def listar(self):       return self.repo.listar_ternas()
    def obtener(self, id_): return self.repo.obtener_terna(id_)
    def estado_activa(self): return EstadoTerna.ACTIVA
