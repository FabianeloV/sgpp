"""
modelo/permisos.py
Matriz de permisos declarativa: ÚNICA fuente de verdad de qué puede ver y hacer
cada rol — secciones del menú, modo solo-lectura, capacidades de flujo y scope de
datos por fila. Tanto el ocultado del menú como el filtrado de datos leen de aquí,
de modo que no pueden desincronizarse.
"""

from .rol_usuario import RolUsuario
from .estado_oferta import EstadoOferta

# ── Índices de sección (coinciden con el orden del QStackedWidget en MainWindow) ──
DASHBOARD     = 0
ESTUDIANTES   = 1
EMPRESAS      = 2
OFERTAS       = 3
POSTULACIONES = 4
TERNAS        = 5
PRACTICAS     = 6
TUTORES       = 7
COORDINADORES = 8
SOLICITUDES   = 9
USUARIOS      = 10
REPORTES      = 11

TODAS_SECCIONES = set(range(12))

# ── Capacidades (verbos de flujo que habilitan botones de acción) ───────────────
CREAR_POSTULACION    = "crear_postulacion"
VALIDAR_POSTULACION  = "validar_postulacion"
RECHAZAR_POSTULACION = "rechazar_postulacion"
ATERNA_POSTULACION   = "aterna_postulacion"
ACEPTAR_POSTULACION  = "aceptar_postulacion"
ENVIAR_TERNA         = "enviar_terna"
CREAR_PRACTICA       = "crear_practica"
FINALIZAR_PRACTICA   = "finalizar_practica"
APROBAR_PRACTICA     = "aprobar_practica"
VALIDAR_ACTIVIDAD    = "validar_actividad"
GESTIONAR_FORMULARIO = "gestionar_formulario"


# ── Predicados de scope por fila: (item, ref_id, repo) -> bool ──────────────────
def _oferta_de_empresa(o, ref_id, repo):
    return getattr(o, "id_empresa", None) == ref_id

def _oferta_activa(o, ref_id, repo):
    return o.estado == EstadoOferta.ACTIVA

def _terna_de_empresa(t, ref_id, repo):
    of = repo.obtener_oferta(t.id_oferta)
    return of is not None and getattr(of, "id_empresa", None) == ref_id

def _practica_de_empresa(p, ref_id, repo):
    post = repo.obtener_postulacion(p.id_postulacion)
    if post is None:
        return False
    of = repo.obtener_oferta(post.id_oferta)
    return of is not None and getattr(of, "id_empresa", None) == ref_id

def _practica_de_tutor(p, ref_id, repo):
    return p.id_t_academico == ref_id or p.id_t_empresarial == ref_id

def _empresa_propia(e, ref_id, repo):
    return e.id_empresa == ref_id


# ── Matriz declarativa: rol -> reglas ───────────────────────────────────────────
# Mapeo Rol -> secciones EXACTO según el requerimiento del usuario.
MATRIZ = {
    RolUsuario.ADMINISTRADOR: {
        "secciones": set(TODAS_SECCIONES),
        "solo_lectura": set(),
        "capacidades": set(),   # admin no se valida por capacidad: puede() devuelve True
        "scope": {},            # admin no filtra: filtrar() devuelve los items intactos
    },
    RolUsuario.COORDINADOR: {
        "secciones": {DASHBOARD, ESTUDIANTES, POSTULACIONES, TERNAS, PRACTICAS, TUTORES, SOLICITUDES, REPORTES},
        "solo_lectura": set(),
        "capacidades": {
            CREAR_POSTULACION, VALIDAR_POSTULACION, RECHAZAR_POSTULACION, ATERNA_POSTULACION,
            ACEPTAR_POSTULACION, ENVIAR_TERNA, CREAR_PRACTICA, FINALIZAR_PRACTICA,
            APROBAR_PRACTICA, VALIDAR_ACTIVIDAD, GESTIONAR_FORMULARIO,
        },
        "scope": {},   # flujo académico global: ve todo para poder gestionarlo
    },
    RolUsuario.EMPRESA: {
        "secciones": {DASHBOARD, OFERTAS, TERNAS, TUTORES},
        "solo_lectura": set(),
        "capacidades": set(),   # gestiona ofertas/tutores por CRUD de sección; ternas en solo-lectura
        "scope": {
            OFERTAS: _oferta_de_empresa,
            TERNAS: _terna_de_empresa,
            PRACTICAS: _practica_de_empresa,   # defensa en profundidad (no está en su menú)
            EMPRESAS: _empresa_propia,         # defensa en profundidad
        },
    },
    RolUsuario.TUTOR: {
        "secciones": {DASHBOARD, ESTUDIANTES, POSTULACIONES, TERNAS},
        "solo_lectura": set(),
        "capacidades": {
            CREAR_POSTULACION, VALIDAR_POSTULACION, RECHAZAR_POSTULACION, ATERNA_POSTULACION,
        },
        "scope": {
            PRACTICAS: _practica_de_tutor,   # defensa en profundidad (no está en su menú)
        },
    },
    RolUsuario.ESTUDIANTE: {
        "secciones": {OFERTAS},
        "solo_lectura": {OFERTAS},
        "capacidades": set(),
        "scope": {
            OFERTAS: _oferta_activa,
        },
    },
}


def _regla(rol):
    return MATRIZ.get(rol)


def secciones_visibles(rol) -> list:
    """Lista ordenada de índices de sección visibles para el rol."""
    r = _regla(rol)
    return sorted(r["secciones"]) if r else []


def puede_ver(rol, seccion_idx) -> bool:
    r = _regla(rol)
    return bool(r) and seccion_idx in r["secciones"]


def es_solo_lectura(rol, seccion_idx) -> bool:
    r = _regla(rol)
    return bool(r) and seccion_idx in r["solo_lectura"]


def puede(rol, capacidad) -> bool:
    """¿El rol tiene la capacidad de flujo? Administrador siempre puede."""
    if rol == RolUsuario.ADMINISTRADOR:
        return True
    r = _regla(rol)
    return bool(r) and capacidad in r["capacidades"]


def filtrar(rol, seccion_idx, items, ref_id, repo) -> list:
    """Aplica el scope por fila de (rol, sección). Administrador no filtra.

    Devuelve lista vacía si el rol es desconocido (sin sesión): así un fallo de
    propagación de sesión nunca expone datos.
    """
    if rol == RolUsuario.ADMINISTRADOR:
        return list(items)
    r = _regla(rol)
    if not r:
        return []
    pred = r["scope"].get(seccion_idx)
    if pred is None:
        return list(items)
    return [it for it in items if pred(it, ref_id, repo)]
