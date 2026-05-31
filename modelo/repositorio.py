"""
modelo/repositorio.py
Repositorio Singleton – persistencia con Pickle.
"""

import os
import pickle
from typing import Dict, List, Optional

from .entidades import (
    Empresa, Convenio, OfertaPractica,
    TutorAcademico, TutorEmpresarial,
    Coordinador, Estudiante,
    Postulacion, Terna, Practica,
    Actividad, Formulario, Documento,
    SolicitudAutorizacion,
    EstadoPractica, EstadoPostulacion,
)

DATA_FILE = os.path.join("data", "sgpp_data.pkl")


class Repositorio:
    """Singleton que almacena y persiste todas las entidades del sistema."""

    _instance: Optional["Repositorio"] = None

    def __new__(cls) -> "Repositorio":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._ready = False
        return cls._instance

    def __init__(self):
        if self._ready:
            return
        self._ready = True
        os.makedirs("data", exist_ok=True)

        # colecciones en memoria
        self.empresas:             Dict[str, Empresa]              = {}
        self.convenios:            Dict[str, Convenio]             = {}
        self.ofertas:              Dict[str, OfertaPractica]       = {}
        self.tutores_academicos:   Dict[str, TutorAcademico]       = {}
        self.tutores_empresariales:Dict[str, TutorEmpresarial]     = {}
        self.coordinadores:        Dict[str, Coordinador]          = {}
        self.estudiantes:          Dict[str, Estudiante]           = {}
        self.postulaciones:        Dict[str, Postulacion]          = {}
        self.ternas:               Dict[str, Terna]                = {}
        self.practicas:            Dict[str, Practica]             = {}
        self.actividades:          Dict[str, Actividad]            = {}
        self.formularios:          Dict[str, Formulario]           = {}
        self.documentos:           Dict[str, Documento]            = {}
        self.solicitudes:          Dict[str, SolicitudAutorizacion]= {}

        self._cargar()

    # ── persistencia ─────────────────────────────────────────────────────────

    _CLAVES = [
        "empresas", "convenios", "ofertas",
        "tutores_academicos", "tutores_empresariales",
        "coordinadores", "estudiantes",
        "postulaciones", "ternas", "practicas",
        "actividades", "formularios", "documentos", "solicitudes",
    ]

    def guardar(self):
        data = {k: getattr(self, k) for k in self._CLAVES}
        with open(DATA_FILE, "wb") as f:
            pickle.dump(data, f)

    def _cargar(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "rb") as f:
                data = pickle.load(f)
            for key in self._CLAVES:
                if key in data:
                    setattr(self, key, data[key])
        except Exception as exc:
            print(f"[Repositorio] Error al cargar datos: {exc}")

    # ── helpers genéricos ─────────────────────────────────────────────────────

    def _set(self, col: dict, key: str, obj):
        col[key] = obj
        self.guardar()

    def _del(self, col: dict, key: str) -> bool:
        if key in col:
            del col[key]
            self.guardar()
            return True
        return False

    # ── EMPRESA ───────────────────────────────────────────────────────────────

    def agregar_empresa(self, e: Empresa):          self._set(self.empresas, e.id_empresa, e)
    def actualizar_empresa(self, e: Empresa):       self._set(self.empresas, e.id_empresa, e)
    def eliminar_empresa(self, id_: str) -> bool:   return self._del(self.empresas, id_)
    def obtener_empresa(self, id_: str) -> Optional[Empresa]: return self.empresas.get(id_)
    def listar_empresas(self) -> List[Empresa]:     return list(self.empresas.values())

    # ── CONVENIO ──────────────────────────────────────────────────────────────

    def agregar_convenio(self, c: Convenio):        self._set(self.convenios, c.id_convenio, c)
    def actualizar_convenio(self, c: Convenio):     self._set(self.convenios, c.id_convenio, c)
    def eliminar_convenio(self, id_: str) -> bool:  return self._del(self.convenios, id_)
    def obtener_convenio(self, id_: str) -> Optional[Convenio]: return self.convenios.get(id_)
    def listar_convenios(self) -> List[Convenio]:   return list(self.convenios.values())

    def convenios_empresa(self, id_empresa: str) -> List[Convenio]:
        return [c for c in self.convenios.values() if c.id_empresa == id_empresa]

    def tiene_convenio_vigente(self, id_empresa: str) -> bool:
        return any(c.esta_vigente() for c in self.convenios_empresa(id_empresa))

    # ── OFERTA ────────────────────────────────────────────────────────────────

    def agregar_oferta(self, o: OfertaPractica):       self._set(self.ofertas, o.id_oferta, o)
    def actualizar_oferta(self, o: OfertaPractica):    self._set(self.ofertas, o.id_oferta, o)
    def eliminar_oferta(self, id_: str) -> bool:       return self._del(self.ofertas, id_)
    def obtener_oferta(self, id_: str) -> Optional[OfertaPractica]: return self.ofertas.get(id_)
    def listar_ofertas(self) -> List[OfertaPractica]:  return list(self.ofertas.values())

    def ofertas_empresa(self, id_empresa: str) -> List[OfertaPractica]:
        return [o for o in self.ofertas.values() if o.id_empresa == id_empresa]

    # ── TUTOR ACADÉMICO ───────────────────────────────────────────────────────

    def agregar_t_academico(self, t: TutorAcademico):    self._set(self.tutores_academicos, t.id_tutor, t)
    def actualizar_t_academico(self, t: TutorAcademico): self._set(self.tutores_academicos, t.id_tutor, t)
    def eliminar_t_academico(self, id_: str) -> bool:    return self._del(self.tutores_academicos, id_)
    def obtener_t_academico(self, id_: str) -> Optional[TutorAcademico]: return self.tutores_academicos.get(id_)
    def listar_t_academicos(self) -> List[TutorAcademico]: return list(self.tutores_academicos.values())

    # ── TUTOR EMPRESARIAL ─────────────────────────────────────────────────────

    def agregar_t_empresarial(self, t: TutorEmpresarial):    self._set(self.tutores_empresariales, t.id_tutor, t)
    def actualizar_t_empresarial(self, t: TutorEmpresarial): self._set(self.tutores_empresariales, t.id_tutor, t)
    def eliminar_t_empresarial(self, id_: str) -> bool:      return self._del(self.tutores_empresariales, id_)
    def obtener_t_empresarial(self, id_: str) -> Optional[TutorEmpresarial]: return self.tutores_empresariales.get(id_)
    def listar_t_empresariales(self) -> List[TutorEmpresarial]: return list(self.tutores_empresariales.values())

    # ── COORDINADOR ───────────────────────────────────────────────────────────

    def agregar_coordinador(self, c: Coordinador):     self._set(self.coordinadores, c.id_coordinador, c)
    def actualizar_coordinador(self, c: Coordinador):  self._set(self.coordinadores, c.id_coordinador, c)
    def eliminar_coordinador(self, id_: str) -> bool:  return self._del(self.coordinadores, id_)
    def obtener_coordinador(self, id_: str) -> Optional[Coordinador]: return self.coordinadores.get(id_)
    def listar_coordinadores(self) -> List[Coordinador]: return list(self.coordinadores.values())

    # ── ESTUDIANTE ────────────────────────────────────────────────────────────

    def agregar_estudiante(self, e: Estudiante):     self._set(self.estudiantes, e.id_estudiante, e)
    def actualizar_estudiante(self, e: Estudiante):  self._set(self.estudiantes, e.id_estudiante, e)
    def eliminar_estudiante(self, id_: str) -> bool: return self._del(self.estudiantes, id_)
    def obtener_estudiante(self, id_: str) -> Optional[Estudiante]: return self.estudiantes.get(id_)
    def listar_estudiantes(self) -> List[Estudiante]: return list(self.estudiantes.values())

    # ── POSTULACION ───────────────────────────────────────────────────────────

    def agregar_postulacion(self, p: Postulacion):     self._set(self.postulaciones, p.id_postulacion, p)
    def actualizar_postulacion(self, p: Postulacion):  self._set(self.postulaciones, p.id_postulacion, p)
    def eliminar_postulacion(self, id_: str) -> bool:  return self._del(self.postulaciones, id_)
    def obtener_postulacion(self, id_: str) -> Optional[Postulacion]: return self.postulaciones.get(id_)
    def listar_postulaciones(self) -> List[Postulacion]: return list(self.postulaciones.values())

    def postulaciones_estudiante(self, id_est: str) -> List[Postulacion]:
        return [p for p in self.postulaciones.values() if p.id_estudiante == id_est]

    def postulaciones_oferta(self, id_of: str) -> List[Postulacion]:
        return [p for p in self.postulaciones.values() if p.id_oferta == id_of]

    # ── TERNA ─────────────────────────────────────────────────────────────────

    def agregar_terna(self, t: Terna):     self._set(self.ternas, t.id_terna, t)
    def actualizar_terna(self, t: Terna):  self._set(self.ternas, t.id_terna, t)
    def eliminar_terna(self, id_: str) -> bool: return self._del(self.ternas, id_)
    def obtener_terna(self, id_: str) -> Optional[Terna]: return self.ternas.get(id_)
    def listar_ternas(self) -> List[Terna]: return list(self.ternas.values())

    def terna_de_oferta(self, id_oferta: str) -> Optional[Terna]:
        for t in self.ternas.values():
            if t.id_oferta == id_oferta:
                return t
        return None

    # ── PRACTICA ─────────────────────────────────────────────────────────────

    def agregar_practica(self, p: Practica):     self._set(self.practicas, p.id_practica, p)
    def actualizar_practica(self, p: Practica):  self._set(self.practicas, p.id_practica, p)
    def eliminar_practica(self, id_: str) -> bool: return self._del(self.practicas, id_)
    def obtener_practica(self, id_: str) -> Optional[Practica]: return self.practicas.get(id_)
    def listar_practicas(self) -> List[Practica]: return list(self.practicas.values())

    def practica_de_postulacion(self, id_post: str) -> Optional[Practica]:
        for p in self.practicas.values():
            if p.id_postulacion == id_post:
                return p
        return None

    def tiene_practica_activa(self, id_estudiante: str) -> bool:
        for p in self.practicas.values():
            post = self.obtener_postulacion(p.id_postulacion)
            if post and post.id_estudiante == id_estudiante and p.estado == EstadoPractica.ACTIVA:
                return True
        return False

    # ── ACTIVIDAD ─────────────────────────────────────────────────────────────

    def agregar_actividad(self, a: Actividad):     self._set(self.actividades, a.id_actividad, a)
    def actualizar_actividad(self, a: Actividad):  self._set(self.actividades, a.id_actividad, a)
    def eliminar_actividad(self, id_: str) -> bool: return self._del(self.actividades, id_)
    def obtener_actividad(self, id_: str) -> Optional[Actividad]: return self.actividades.get(id_)
    def actividades_practica(self, id_prac: str) -> List[Actividad]:
        return [a for a in self.actividades.values() if a.id_practica == id_prac]

    # ── FORMULARIO ────────────────────────────────────────────────────────────

    def agregar_formulario(self, f: Formulario):    self._set(self.formularios, f.id_formulario, f)
    def actualizar_formulario(self, f: Formulario): self._set(self.formularios, f.id_formulario, f)
    def eliminar_formulario(self, id_: str) -> bool: return self._del(self.formularios, id_)
    def obtener_formulario(self, id_: str) -> Optional[Formulario]: return self.formularios.get(id_)
    def formularios_practica(self, id_prac: str) -> List[Formulario]:
        return [f for f in self.formularios.values() if f.id_practica == id_prac]

    # ── DOCUMENTO ─────────────────────────────────────────────────────────────

    def agregar_documento(self, d: Documento):     self._set(self.documentos, d.id_documento, d)
    def actualizar_documento(self, d: Documento):  self._set(self.documentos, d.id_documento, d)
    def eliminar_documento(self, id_: str) -> bool: return self._del(self.documentos, id_)
    def documentos_practica(self, id_prac: str) -> List[Documento]:
        return [d for d in self.documentos.values() if d.id_practica == id_prac]

    # ── SOLICITUD ─────────────────────────────────────────────────────────────

    def agregar_solicitud(self, s: SolicitudAutorizacion):     self._set(self.solicitudes, s.id_solicitud, s)
    def actualizar_solicitud(self, s: SolicitudAutorizacion):  self._set(self.solicitudes, s.id_solicitud, s)
    def eliminar_solicitud(self, id_: str) -> bool:            return self._del(self.solicitudes, id_)
    def obtener_solicitud(self, id_: str) -> Optional[SolicitudAutorizacion]: return self.solicitudes.get(id_)
    def listar_solicitudes(self) -> List[SolicitudAutorizacion]: return list(self.solicitudes.values())

    def solicitudes_estudiante(self, id_est: str) -> List[SolicitudAutorizacion]:
        return [s for s in self.solicitudes.values() if s.id_estudiante == id_est]
