"""
Controlador principal de la aplicación.

Centraliza el arranque, la creación de controladores secundarios, la carga de
datos iniciales y la construcción de la ventana principal.
"""

import os
import sys
from dataclasses import dataclass

from modelo.entidades import (
    Convenio,
    Coordinador,
    Empresa,
    EstadoOferta,
    EstadoPostulacion,
    EstadoPractica,
    EstadoSolicitud,
    EstadoTerna,
    Estudiante,
    OfertaPractica,
    TutorAcademico,
    TutorEmpresarial,
)
from modelo.repositorio import Repositorio

from .controlador_convenio import ControladorConvenio
from .controlador_coordinador import ControladorCoordinador
from .controlador_empresa import ControladorEmpresa
from .controlador_estudiante import ControladorEstudiante
from .controlador_oferta import ControladorOferta
from .controlador_postulacion import ControladorPostulacion
from .controlador_practica import ControladorPractica
from .controlador_solicitud import ControladorSolicitud
from .controlador_terna import ControladorTerna
from .controlador_tutor import ControladorTutor


@dataclass
class ControladoresAplicacion:
    empresa: ControladorEmpresa
    convenio: ControladorConvenio
    oferta: ControladorOferta
    tutor: ControladorTutor
    coordinador: ControladorCoordinador
    estudiante: ControladorEstudiante
    postulacion: ControladorPostulacion
    terna: ControladorTerna
    practica: ControladorPractica
    solicitud: ControladorSolicitud


class ControladorPrincipal:
    def __init__(self, argv=None, directorio_proyecto: str | None = None):
        self.argv = argv or sys.argv
        self.directorio_proyecto = directorio_proyecto or os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.repo = Repositorio()
        self.controladores = ControladoresAplicacion(
            empresa=ControladorEmpresa(),
            convenio=ControladorConvenio(),
            oferta=ControladorOferta(),
            tutor=ControladorTutor(),
            coordinador=ControladorCoordinador(),
            estudiante=ControladorEstudiante(),
            postulacion=ControladorPostulacion(),
            terna=ControladorTerna(),
            practica=ControladorPractica(),
            solicitud=ControladorSolicitud(),
        )
        self.app = None
        self.ventana = None

    def ejecutar(self) -> int:
        os.chdir(self.directorio_proyecto)

        from PyQt6.QtGui import QFont
        from PyQt6.QtWidgets import QApplication
        from vista.main_window import MainWindow

        self.app = QApplication(self.argv)
        self.app.setApplicationName("SGPP")
        self.app.setOrganizationName("Universidad de Cuenca")

        fuente = QFont("Segoe UI", 10)
        fuente.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
        self.app.setFont(fuente)
        self.app.setStyleSheet(self._estilo_global())

        self.cargar_datos_demo()

        self.ventana = MainWindow()
        self.ventana.show()

        return self.app.exec()

    def cargar_datos_demo(self):
        """Inserta datos de ejemplo si la base está vacía, para demostración."""
        if self.repo.listar_empresas():
            return

        e1 = Empresa(nombre="Etapa EP",         RUC="0160000550001")
        e2 = Empresa(nombre="Tecniseguros S.A.", RUC="0190012345001")
        e3 = Empresa(nombre="Banco del Austro",  RUC="0190001234001")
        for empresa in [e1, e2, e3]:
            self.repo.agregar_empresa(empresa)

        self.repo.agregar_convenio(Convenio("2025-01-01", "2026-12-31", e1.id_empresa))
        self.repo.agregar_convenio(Convenio("2024-06-01", "2025-05-31", e2.id_empresa))

        coord = Coordinador(
            nombre="Laura", apellido="Vásquez",
            correo="lvasquez@ucuenca.edu.ec",
            telefono="0987654321", cedula="0102030405",
        )
        self.repo.agregar_coordinador(coord)

        ta = TutorAcademico(
            nombre="Carlos", apellido="Cárdenas",
            correo="ccardenas@ucuenca.edu.ec",
            telefono="0991122334", area="Ingeniería de Software",
        )
        te = TutorEmpresarial(
            nombre="Marco", apellido="Peñafiel",
            correo="mpenafiel@etapa.net.ec",
            telefono="0998877665", cargo="Jefe de Sistemas",
        )
        self.repo.agregar_t_academico(ta)
        self.repo.agregar_t_empresarial(te)

        ofertas = [
            OfertaPractica(
                descripcion="Desarrollo de aplicaciones web con Java/Jakarta EE",
                requisitos="Ciclo ≥ 6, conocimientos de Java y bases de datos relacionales.",
                id_empresa=e1.id_empresa,
            ),
            OfertaPractica(
                descripcion="Soporte técnico y administración de redes",
                requisitos="Ciclo ≥ 6, conocimientos de redes y sistemas operativos.",
                id_empresa=e1.id_empresa,
            ),
            OfertaPractica(
                descripcion="Desarrollo de sistemas de información para seguros",
                requisitos="Ciclo ≥ 7, Python o Java, bases de datos.",
                id_empresa=e2.id_empresa,
            ),
        ]
        for oferta in ofertas:
            self.repo.agregar_oferta(oferta)

        estudiantes_data = [
            ("Ana",      "Torres",   "atorres@ucuenca.edu.ec",  "0981234560", 6,  False),
            ("Pedro",    "Mora",     "pmora@ucuenca.edu.ec",    "0972345671", 7,  False),
            ("Sofía",    "Quizhpi",  "squizhpi@ucuenca.edu.ec", "0963456782", 8,  True),
            ("Diego",    "Ávila",    "davila@ucuenca.edu.ec",   "0954567893", 6,  False),
            ("Valentina","Parra",    "vparra@ucuenca.edu.ec",   "0945678904", 9,  True),
            ("Luis",     "Correa",   "lcorrea@ucuenca.edu.ec",  "0936789015", 5,  False),
        ]
        for nom, ape, cor, tel, ciclo, prev in estudiantes_data:
            estudiante = Estudiante(
                nombre=nom, apellido=ape, correo=cor, telefono=tel,
                ciclo=ciclo, malla="Computación 2021",
                CV=f"CV_{nom}_{ape}.pdf", tiene_practica_previa=prev,
            )
            self.repo.agregar_estudiante(estudiante)

        self.repo.guardar()
        print("[SGPP] Datos de demostración cargados correctamente.")

    def obtener_resumen_dashboard(self) -> dict:
        practicas = self.repo.listar_practicas()
        estudiantes = self.repo.listar_estudiantes()
        empresas = self.repo.listar_empresas()
        ofertas = self.repo.listar_ofertas()
        posts = self.repo.listar_postulaciones()
        ternas = self.repo.listar_ternas()
        solicitudes = self.repo.listar_solicitudes()

        act_prac = [p for p in practicas if p.estado == EstadoPractica.ACTIVA]
        pend_post = [p for p in posts if p.estado == EstadoPostulacion.PENDIENTE]
        pend_ter = [t for t in ternas if t.estado == EstadoTerna.ACTIVA]
        pend_sol = [s for s in solicitudes if s.estado == EstadoSolicitud.PENDIENTE]

        return {
            "stats": [
                ("Estudiantes", str(len(estudiantes)), "#1B4F8A", "👩‍🎓"),
                ("Empresas", str(len(empresas)), "#1565C0", "🏢"),
                (
                    "Ofertas Activas",
                    str(sum(1 for o in ofertas if o.estado == EstadoOferta.ACTIVA)),
                    "#2E7D32",
                    "📋",
                ),
                ("Postul. Pendientes", str(len(pend_post)), "#E65100", "📝"),
                ("Prácticas Activas", str(len(act_prac)), "#6A1B9A", "🎓"),
                ("Solicitudes Pend.", str(len(pend_sol)), "#C62828", "📩"),
            ],
            "practicas_activas": self._filas_practicas_activas(act_prac),
            "postulaciones_pendientes": self._filas_postulaciones_pendientes(pend_post),
            "ternas_pendientes": self._filas_ternas_pendientes(pend_ter),
            "solicitudes_pendientes": self._filas_solicitudes_pendientes(pend_sol),
        }

    def _filas_practicas_activas(self, practicas):
        filas = []
        for practica in practicas:
            post = self.repo.obtener_postulacion(practica.id_postulacion)
            est = self.repo.obtener_estudiante(post.id_estudiante) if post else None
            oferta = self.repo.obtener_oferta(post.id_oferta) if post else None
            empresa = self.repo.obtener_empresa(oferta.id_empresa) if oferta else None
            filas.append([
                practica.id_practica,
                est.nombre_completo if est else "?",
                empresa.nombre if empresa else "?",
                practica.fecha_inicio,
            ])
        return filas

    def _filas_postulaciones_pendientes(self, postulaciones):
        filas = []
        for post in postulaciones[:15]:
            estudiante = self.repo.obtener_estudiante(post.id_estudiante)
            oferta = self.repo.obtener_oferta(post.id_oferta)
            filas.append([
                post.id_postulacion,
                estudiante.nombre_completo if estudiante else "?",
                oferta.descripcion[:40] if oferta else "?",
                post.fecha,
            ])
        return filas

    def _filas_ternas_pendientes(self, ternas):
        filas = []
        for terna in ternas:
            oferta = self.repo.obtener_oferta(terna.id_oferta)
            filas.append([
                terna.id_terna,
                oferta.descripcion[:40] if oferta else "?",
                len(terna.id_postulaciones),
            ])
        return filas

    def _filas_solicitudes_pendientes(self, solicitudes):
        filas = []
        for solicitud in solicitudes[:15]:
            estudiante = self.repo.obtener_estudiante(solicitud.id_estudiante)
            filas.append([
                solicitud.id_solicitud,
                estudiante.nombre_completo if estudiante else "?",
                solicitud.tipo,
                solicitud.fecha,
            ])
        return filas

    def _estilo_global(self) -> str:
        return """
            QWidget {
                font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            }
            QScrollArea { border: none; }
            QToolTip {
                background-color: #1B4F8A; color: white;
                border: 1px solid #0D3166; padding: 4px;
            }
            QMessageBox { background-color: #FFFFFF; }
            QDialogButtonBox QPushButton {
                min-width: 90px; min-height: 30px;
            }
        """


def main() -> int:
    return ControladorPrincipal().ejecutar()
