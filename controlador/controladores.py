"""
Fachada de compatibilidad para los controladores del paquete.

Cada implementación vive en su propio módulo dentro de controlador/.
"""

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


R = Repositorio  # alias preservado por compatibilidad

__all__ = [
    "ControladorEmpresa",
    "ControladorConvenio",
    "ControladorOferta",
    "ControladorTutor",
    "ControladorCoordinador",
    "ControladorEstudiante",
    "ControladorPostulacion",
    "ControladorTerna",
    "ControladorPractica",
    "ControladorSolicitud",
    "R",
]
