from datetime import date
from typing import Optional, Tuple

from modelo.entidades import EstadoSolicitud, SolicitudAutorizacion
from modelo.repositorio import Repositorio


class ControladorSolicitud:
    def __init__(self): self.repo = Repositorio()

    def agregar(self, id_estudiante: str, tipo: str,
                id_empresa: Optional[str] = None) -> Tuple[bool, str]:
        if not self.repo.obtener_estudiante(id_estudiante):
            return False, "Estudiante no encontrado."
        s = SolicitudAutorizacion(
            id_estudiante=id_estudiante,
            tipo=tipo,
            fecha=date.today().isoformat(),
            id_empresa=id_empresa,
        )
        self.repo.agregar_solicitud(s)
        return True, f"Solicitud registrada (ID: {s.id_solicitud})."

    def resolver(self, id_: str, estado: str, id_coordinador: str,
                 obs: str = "") -> Tuple[bool, str]:
        s = self.repo.obtener_solicitud(id_)
        if not s: return False, "Solicitud no encontrada."
        if s.estado != EstadoSolicitud.PENDIENTE:
            return False, "La solicitud ya fue resuelta."
        s.estado = estado
        s.id_coordinador = id_coordinador
        s.observaciones = obs
        self.repo.actualizar_solicitud(s)
        return True, f"Solicitud marcada como '{estado}'."

    def eliminar(self, id_: str) -> Tuple[bool, str]:
        self.repo.eliminar_solicitud(id_)
        return True, "Solicitud eliminada."

    def listar(self):       return self.repo.listar_solicitudes()
    def obtener(self, id_): return self.repo.obtener_solicitud(id_)
    def tipos(self):
        from modelo.entidades import TipoSolicitud
        return TipoSolicitud.TODOS
    def estados_resolucion(self):
        return [EstadoSolicitud.APROBADA, EstadoSolicitud.RECHAZADA]
    def estado_pendiente(self): return EstadoSolicitud.PENDIENTE
    def estado_aprobada(self): return EstadoSolicitud.APROBADA
    def estado_rechazada(self): return EstadoSolicitud.RECHAZADA
