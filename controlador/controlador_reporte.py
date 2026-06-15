"""
controlador/controlador_reporte.py
Reúne los datos de los reportes (sin presentación). Devuelve estructuras de datos
planas que la vista convierte a PDF. El "Resumen general" refleja los mismos datos
del dashboard.
"""

from typing import List, Tuple

from modelo.repositorio import Repositorio
from modelo.entidades import (
    EstadoOferta, EstadoPractica, EstadoPostulacion, EstadoTerna, EstadoSolicitud,
)


class ControladorReporte:
    def __init__(self):
        self.repo = Repositorio()

    def disponibles(self) -> List[Tuple[str, str]]:
        """(clave, título) de los reportes ofrecidos."""
        return [
            ("resumen",       "Resumen general (Dashboard)"),
            ("estudiantes",   "Listado de estudiantes"),
            ("practicas",     "Listado de prácticas"),
            ("postulaciones", "Listado de postulaciones"),
        ]

    def generar(self, clave: str) -> dict:
        return {
            "resumen":       self.resumen,
            "estudiantes":   self.estudiantes,
            "practicas":     self.practicas,
            "postulaciones": self.postulaciones,
        }[clave]()

    # ── Resumen general (mismos datos que el dashboard) ─────────────────────────
    def resumen(self) -> dict:
        repo = self.repo
        practicas   = repo.listar_practicas()
        estudiantes = repo.listar_estudiantes()
        empresas    = repo.listar_empresas()
        ofertas     = repo.listar_ofertas()
        posts       = repo.listar_postulaciones()
        ternas      = repo.listar_ternas()
        solicitudes = repo.listar_solicitudes()

        act_prac = [p for p in practicas   if p.estado == EstadoPractica.ACTIVA]
        pend_post= [p for p in posts        if p.estado == EstadoPostulacion.PENDIENTE]
        pend_ter = [t for t in ternas       if t.estado == EstadoTerna.ACTIVA]
        pend_sol = [s for s in solicitudes  if s.estado == EstadoSolicitud.PENDIENTE]
        ofertas_act = [o for o in ofertas   if o.estado == EstadoOferta.ACTIVA]

        filas_prac = []
        for p in act_prac:
            post = repo.obtener_postulacion(p.id_postulacion)
            est  = repo.obtener_estudiante(post.id_estudiante) if post else None
            of   = repo.obtener_oferta(post.id_oferta)         if post else None
            emp  = repo.obtener_empresa(of.id_empresa)          if of   else None
            filas_prac.append([p.id_practica, est.nombre_completo if est else "?",
                               emp.nombre if emp else "?", p.fecha_inicio])

        filas_pp = []
        for p in pend_post:
            est = repo.obtener_estudiante(p.id_estudiante)
            of  = repo.obtener_oferta(p.id_oferta)
            filas_pp.append([p.id_postulacion, est.nombre_completo if est else "?",
                             of.descripcion[:50] if of else "?", p.fecha])

        filas_ter = []
        for t in pend_ter:
            of = repo.obtener_oferta(t.id_oferta)
            filas_ter.append([t.id_terna, of.descripcion[:50] if of else "?",
                              len(t.id_postulaciones)])

        filas_sol = []
        for s in pend_sol:
            est = repo.obtener_estudiante(s.id_estudiante)
            filas_sol.append([s.id_solicitud, est.nombre_completo if est else "?",
                              s.tipo, s.fecha])

        return {
            "titulo": "Resumen General",
            "stats": [
                ("Estudiantes", len(estudiantes)),
                ("Empresas", len(empresas)),
                ("Ofertas activas", len(ofertas_act)),
                ("Postulaciones pendientes", len(pend_post)),
                ("Prácticas activas", len(act_prac)),
                ("Solicitudes pendientes", len(pend_sol)),
            ],
            "tablas": [
                {"titulo": "Prácticas activas",
                 "headers": ["ID", "Estudiante", "Empresa", "Desde"], "filas": filas_prac},
                {"titulo": "Postulaciones pendientes",
                 "headers": ["ID", "Estudiante", "Oferta", "Fecha"], "filas": filas_pp},
                {"titulo": "Ternas pendientes de enviar",
                 "headers": ["ID", "Oferta", "# Post."], "filas": filas_ter},
                {"titulo": "Solicitudes pendientes",
                 "headers": ["ID", "Estudiante", "Tipo", "Fecha"], "filas": filas_sol},
            ],
        }

    # ── Listados completos ──────────────────────────────────────────────────────
    def estudiantes(self) -> dict:
        filas = [[e.id_estudiante, e.nombre_completo, e.correo, e.ciclo,
                  "Sí" if e.tiene_practica_previa else "No"]
                 for e in self.repo.listar_estudiantes()]
        return {"titulo": "Listado de Estudiantes",
                "stats": [("Total", len(filas))],
                "tablas": [{"titulo": "Estudiantes",
                            "headers": ["ID", "Nombre", "Correo", "Ciclo", "Práctica previa"],
                            "filas": filas}]}

    def practicas(self) -> dict:
        repo = self.repo
        filas = []
        for p in repo.listar_practicas():
            post = repo.obtener_postulacion(p.id_postulacion)
            est  = repo.obtener_estudiante(post.id_estudiante) if post else None
            filas.append([p.id_practica, est.nombre_completo if est else "?",
                          p.estado, p.fecha_inicio, p.fecha_fin or "—"])
        return {"titulo": "Listado de Prácticas",
                "stats": [("Total", len(filas))],
                "tablas": [{"titulo": "Prácticas",
                            "headers": ["ID", "Estudiante", "Estado", "Inicio", "Fin"],
                            "filas": filas}]}

    def postulaciones(self) -> dict:
        repo = self.repo
        filas = []
        for p in repo.listar_postulaciones():
            est = repo.obtener_estudiante(p.id_estudiante)
            of  = repo.obtener_oferta(p.id_oferta)
            filas.append([p.id_postulacion, est.nombre_completo if est else "?",
                          of.descripcion[:50] if of else "?", p.estado, p.fecha])
        return {"titulo": "Listado de Postulaciones",
                "stats": [("Total", len(filas))],
                "tablas": [{"titulo": "Postulaciones",
                            "headers": ["ID", "Estudiante", "Oferta", "Estado", "Fecha"],
                            "filas": filas}]}
