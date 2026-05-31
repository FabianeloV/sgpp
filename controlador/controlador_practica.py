from typing import Tuple

from modelo.entidades import (
    Actividad,
    EstadoPostulacion,
    EstadoPractica,
    Formulario,
    Practica,
    TipoFormulario,
)
from modelo.repositorio import Repositorio


class ControladorPractica:
    def __init__(self): self.repo = Repositorio()

    def crear(self, id_postulacion: str, id_t_academico: str,
              id_t_empresarial: str, fecha_inicio: str) -> Tuple[bool, str]:
        post = self.repo.obtener_postulacion(id_postulacion)
        if not post: return False, "Postulación no encontrada."
        if post.estado != EstadoPostulacion.ACEPTADA:
            return False, "Solo postulaciones aceptadas pueden generar una práctica."
        if self.repo.practica_de_postulacion(id_postulacion):
            return False, "Esta postulación ya tiene una práctica asociada."
        if not self.repo.obtener_t_academico(id_t_academico):
            return False, "Tutor académico no encontrado."
        if not self.repo.obtener_t_empresarial(id_t_empresarial):
            return False, "Tutor empresarial no encontrado."
        if self.repo.tiene_practica_activa(post.id_estudiante):
            return False, "El estudiante ya tiene una práctica activa."
        p = Practica(
            fecha_inicio=fecha_inicio,
            id_postulacion=id_postulacion,
            id_t_academico=id_t_academico,
            id_t_empresarial=id_t_empresarial,
        )
        self.repo.agregar_practica(p)
        # Crear Formulario 1 automáticamente
        f1 = Formulario(tipo=TipoFormulario.F1, fecha=fecha_inicio, id_practica=p.id_practica)
        self.repo.agregar_formulario(f1)
        return True, f"Práctica creada (ID: {p.id_practica}). Formulario 1 generado automáticamente."

    def finalizar(self, id_: str, fecha_fin: str, observaciones: str = "") -> Tuple[bool, str]:
        p = self.repo.obtener_practica(id_)
        if not p: return False, "Práctica no encontrada."
        if p.estado != EstadoPractica.ACTIVA:
            return False, "Solo se pueden finalizar prácticas activas."
        p.estado = EstadoPractica.FINALIZADA
        p.fecha_fin = fecha_fin
        p.observaciones = observaciones
        self.repo.actualizar_practica(p)
        return True, "Práctica finalizada. Proceda a completar los Formularios 2 y 3."

    def aprobar(self, id_: str) -> Tuple[bool, str]:
        """Aprobación oficial: requiere F2 y F3 firmados, y F1 firmado."""
        p = self.repo.obtener_practica(id_)
        if not p: return False, "Práctica no encontrada."
        if p.estado != EstadoPractica.FINALIZADA:
            return False, "Solo se pueden aprobar prácticas finalizadas."
        forms = {f.tipo: f for f in self.repo.formularios_practica(id_)}
        faltantes = []
        for tipo in [TipoFormulario.F1, TipoFormulario.F2, TipoFormulario.F3]:
            if tipo not in forms:
                faltantes.append(TipoFormulario.NOMBRES[tipo])
        if faltantes:
            return False, f"Faltan formularios: {', '.join(faltantes)}."
        p.estado = EstadoPractica.APROBADA
        self.repo.actualizar_practica(p)
        # Marcar práctica previa al estudiante
        post = self.repo.obtener_postulacion(p.id_postulacion)
        if post:
            est = self.repo.obtener_estudiante(post.id_estudiante)
            if est:
                est.tiene_practica_previa = True
                self.repo.actualizar_estudiante(est)
        return True, "Práctica aprobada oficialmente."

    def eliminar(self, id_: str) -> Tuple[bool, str]:
        self.repo.eliminar_practica(id_)
        return True, "Práctica eliminada."

    def listar(self):       return self.repo.listar_practicas()
    def obtener(self, id_): return self.repo.obtener_practica(id_)
    def estado_activa(self): return EstadoPractica.ACTIVA
    def estado_finalizada(self): return EstadoPractica.FINALIZADA
    def estado_aprobada(self): return EstadoPractica.APROBADA
    def estado_suspendida(self): return EstadoPractica.SUSPENDIDA
    def estado_postulacion_aceptada(self): return EstadoPostulacion.ACEPTADA
    def tiene_practica_de_postulacion(self, id_postulacion: str) -> bool:
        return self.repo.practica_de_postulacion(id_postulacion) is not None

    # actividades
    def actividades_de_practica(self, id_practica: str):
        return self.repo.actividades_practica(id_practica)

    def agregar_actividad(self, id_practica: str, descripcion: str, fecha: str) -> Tuple[bool, str]:
        if not self.repo.obtener_practica(id_practica):
            return False, "Práctica no encontrada."
        a = Actividad(id_practica=id_practica, descripcion=descripcion.strip(), fecha=fecha)
        self.repo.agregar_actividad(a)
        return True, f"Actividad registrada (ID: {a.id_actividad})."

    def validar_actividad(self, id_act: str, id_tutor: str) -> Tuple[bool, str]:
        a = self.repo.obtener_actividad(id_act)
        if not a: return False, "Actividad no encontrada."
        a.validada = True
        a.id_tutor_valida = id_tutor
        self.repo.actualizar_actividad(a)
        return True, "Actividad validada."

    def eliminar_actividad(self, id_act: str) -> Tuple[bool, str]:
        self.repo.eliminar_actividad(id_act)
        return True, "Actividad eliminada."

    # formularios
    def formularios_de_practica(self, id_practica: str):
        return self.repo.formularios_practica(id_practica)

    def obtener_formulario(self, id_: str):
        return self.repo.obtener_formulario(id_)

    def tipos_formulario(self):
        return TipoFormulario.TODOS

    def nombre_tipo_formulario(self, tipo: int) -> str:
        return TipoFormulario.NOMBRES[tipo]

    def agregar_formulario(self, id_practica: str, tipo: int, fecha: str, firmado: bool,
                           obs: str) -> Tuple[bool, str]:
        p = self.repo.obtener_practica(id_practica)
        if not p: return False, "Práctica no encontrada."
        # Validar unicidad de tipo por práctica
        existentes = self.repo.formularios_practica(id_practica)
        if any(f.tipo == tipo for f in existentes):
            return False, f"Ya existe un {TipoFormulario.NOMBRES[tipo]} para esta práctica."
        if tipo == TipoFormulario.F1 and p.estado != EstadoPractica.ACTIVA:
            return False, "El Formulario 1 solo se puede agregar con práctica activa."
        if tipo in [TipoFormulario.F2, TipoFormulario.F3] and p.estado not in [
            EstadoPractica.FINALIZADA, EstadoPractica.APROBADA
        ]:
            return False, "Los Formularios 2 y 3 se agregan al finalizar la práctica."
        f = Formulario(tipo=tipo, fecha=fecha, id_practica=id_practica, firmado=firmado, observaciones=obs)
        self.repo.agregar_formulario(f)
        return True, f"{TipoFormulario.NOMBRES[tipo]} registrado."

    def actualizar_formulario(self, id_: str, firmado: bool, obs: str) -> Tuple[bool, str]:
        f = self.repo.obtener_formulario(id_)
        if not f: return False, "Formulario no encontrado."
        f.firmado, f.observaciones = firmado, obs
        self.repo.actualizar_formulario(f)
        return True, "Formulario actualizado."

    def eliminar_formulario(self, id_: str) -> Tuple[bool, str]:
        self.repo.eliminar_formulario(id_)
        return True, "Formulario eliminado."
