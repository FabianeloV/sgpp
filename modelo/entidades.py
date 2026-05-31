"""
Fachada de compatibilidad para las entidades del dominio.

Cada clase vive en su propio módulo dentro de modelo/.
"""

from .actividad import Actividad
from .convenio import Convenio
from .coordinador import Coordinador
from .documento import Documento
from .empresa import Empresa
from .estado_oferta import EstadoOferta
from .estado_postulacion import EstadoPostulacion
from .estado_practica import EstadoPractica
from .estado_solicitud import EstadoSolicitud
from .estado_terna import EstadoTerna
from .estudiante import Estudiante
from .formulario import Formulario
from .id_generator import gen_id
from .oferta_practica import OfertaPractica
from .postulacion import Postulacion
from .practica import Practica
from .solicitud_autorizacion import SolicitudAutorizacion
from .terna import Terna
from .tipo_formulario import TipoFormulario
from .tipo_solicitud import TipoSolicitud
from .tutor import Tutor
from .tutor_academico import TutorAcademico
from .tutor_empresarial import TutorEmpresarial


__all__ = [
    "gen_id",
    "EstadoOferta",
    "EstadoPostulacion",
    "EstadoTerna",
    "EstadoPractica",
    "TipoFormulario",
    "TipoSolicitud",
    "EstadoSolicitud",
    "Empresa",
    "Convenio",
    "OfertaPractica",
    "Tutor",
    "TutorAcademico",
    "TutorEmpresarial",
    "Coordinador",
    "Estudiante",
    "Postulacion",
    "Terna",
    "Practica",
    "Actividad",
    "Formulario",
    "Documento",
    "SolicitudAutorizacion",
]
