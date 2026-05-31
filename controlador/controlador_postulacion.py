from datetime import date
from typing import Optional, Tuple

from modelo.entidades import (
    EstadoOferta,
    EstadoPostulacion,
    Postulacion,
    Terna,
)
from modelo.repositorio import Repositorio


class ControladorPostulacion:
    def __init__(self): self.repo = Repositorio()

    def agregar(self, id_estudiante: str, id_oferta: str, id_coordinador: Optional[str] = None) -> Tuple[bool, str]:
        est = self.repo.obtener_estudiante(id_estudiante)
        if not est: return False, "Estudiante no existe."
        if not est.puede_practicas_externas():
            return False, f"El estudiante está en ciclo {est.ciclo}; solo desde 6.° ciclo se permiten prácticas externas."
        oferta = self.repo.obtener_oferta(id_oferta)
        if not oferta: return False, "Oferta no existe."
        if oferta.estado != EstadoOferta.ACTIVA:
            return False, f"La oferta no está activa (estado: {oferta.estado})."
        # Una sola postulación activa por oferta por estudiante
        existentes = self.repo.postulaciones_oferta(id_oferta)
        for p in existentes:
            if p.id_estudiante == id_estudiante and p.estado not in [
                EstadoPostulacion.RECHAZADA
            ]:
                return False, "El estudiante ya tiene una postulación activa a esta oferta."
        p = Postulacion(
            fecha=date.today().isoformat(),
            id_estudiante=id_estudiante,
            id_oferta=id_oferta,
            id_coordinador=id_coordinador,
        )
        self.repo.agregar_postulacion(p)
        return True, f"Postulación registrada (ID: {p.id_postulacion})."

    def validar(self, id_: str, id_coordinador: str) -> Tuple[bool, str]:
        p = self.repo.obtener_postulacion(id_)
        if not p: return False, "Postulación no encontrada."
        if p.estado != EstadoPostulacion.PENDIENTE:
            return False, f"Solo se pueden validar postulaciones en estado Pendiente (actual: {p.estado})."
        p.estado = EstadoPostulacion.VALIDADA
        p.id_coordinador = id_coordinador
        self.repo.actualizar_postulacion(p)
        return True, "Postulación validada."

    def rechazar(self, id_: str, observaciones: str = "") -> Tuple[bool, str]:
        p = self.repo.obtener_postulacion(id_)
        if not p: return False, "Postulación no encontrada."
        p.estado = EstadoPostulacion.RECHAZADA
        p.observaciones = observaciones
        self.repo.actualizar_postulacion(p)
        return True, "Postulación rechazada."

    def actualizar(self, id_: str, id_estudiante: str, id_oferta: str,
                   id_coordinador: Optional[str] = None) -> Tuple[bool, str]:
        p = self.repo.obtener_postulacion(id_)
        if not p: return False, "Postulación no encontrada."
        if p.estado != EstadoPostulacion.PENDIENTE:
            return False, "Solo se pueden editar postulaciones pendientes."
        if not self.repo.obtener_estudiante(id_estudiante):
            return False, "Estudiante no existe."
        if not self.repo.obtener_oferta(id_oferta):
            return False, "Oferta no existe."
        for existente in self.repo.postulaciones_oferta(id_oferta):
            if (
                existente.id_postulacion != id_
                and existente.id_estudiante == id_estudiante
                and existente.estado != EstadoPostulacion.RECHAZADA
            ):
                return False, "El estudiante ya tiene una postulación activa a esta oferta."
        p.id_estudiante = id_estudiante
        p.id_oferta = id_oferta
        p.id_coordinador = id_coordinador
        self.repo.actualizar_postulacion(p)
        return True, "Postulación actualizada."

    def agregar_a_terna(self, id_postulacion: str) -> Tuple[bool, str]:
        p = self.repo.obtener_postulacion(id_postulacion)
        if not p: return False, "Postulación no encontrada."
        if p.estado != EstadoPostulacion.VALIDADA:
            return False, "Solo se pueden agregar a terna postulaciones validadas."
        terna = self.repo.terna_de_oferta(p.id_oferta)
        if not terna:
            terna = Terna(id_oferta=p.id_oferta)
            self.repo.agregar_terna(terna)
        if terna.esta_completa():
            return False, "La terna ya tiene 3 postulaciones (límite máximo)."
        if not terna.agregar(id_postulacion):
            return False, "La postulación ya está en la terna."
        p.estado = EstadoPostulacion.EN_TERNA
        self.repo.actualizar_postulacion(p)
        self.repo.actualizar_terna(terna)
        return True, "Postulación agregada a la terna."

    def aceptar(self, id_: str) -> Tuple[bool, str]:
        """La empresa selecciona al estudiante de la terna."""
        p = self.repo.obtener_postulacion(id_)
        if not p: return False, "Postulación no encontrada."
        if p.estado != EstadoPostulacion.EN_TERNA:
            return False, "Solo se pueden aceptar postulaciones en terna."
        est = self.repo.obtener_estudiante(p.id_estudiante)
        if est and self.repo.tiene_practica_activa(p.id_estudiante):
            return False, "El estudiante ya tiene una práctica activa."
        p.estado = EstadoPostulacion.ACEPTADA
        self.repo.actualizar_postulacion(p)
        return True, "Postulación aceptada. Ahora puede crearse la práctica."

    def eliminar(self, id_: str) -> Tuple[bool, str]:
        if self.repo.practica_de_postulacion(id_):
            return False, "No se puede eliminar: ya generó una práctica."
        self.repo.eliminar_postulacion(id_)
        return True, "Postulación eliminada."

    def listar(self):       return self.repo.listar_postulaciones()
    def obtener(self, id_): return self.repo.obtener_postulacion(id_)
    def estado_pendiente(self): return EstadoPostulacion.PENDIENTE
    def estado_validada(self): return EstadoPostulacion.VALIDADA
    def estado_en_terna(self): return EstadoPostulacion.EN_TERNA
    def estado_aceptada(self): return EstadoPostulacion.ACEPTADA
    def estado_rechazada(self): return EstadoPostulacion.RECHAZADA
