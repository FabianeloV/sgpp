"""
modelo/sesion.py
Sesión Singleton – usuario autenticado en tiempo de ejecución.

Mismo idiom que Repositorio (singleton vía __new__/_ready), pero NO se persiste:
la sesión vive solo durante la ejecución; no entra en el pickle.
"""

from typing import Optional

from .usuario import Usuario


class Sesion:
    """Singleton de runtime con el usuario autenticado."""

    _instance: Optional["Sesion"] = None

    def __new__(cls) -> "Sesion":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._ready = False
        return cls._instance

    def __init__(self):
        if self._ready:
            return
        self._ready = True
        self.usuario: Optional[Usuario] = None

    # ── estado ──────────────────────────────────────────────────────────────
    def establecer(self, usuario: Usuario):
        self.usuario = usuario

    def limpiar(self):
        self.usuario = None

    # ── conveniencia ────────────────────────────────────────────────────────
    @property
    def rol(self) -> Optional[str]:
        return self.usuario.rol if self.usuario else None

    @property
    def ref_id(self) -> Optional[str]:
        return self.usuario.ref_id if self.usuario else None

    @property
    def activa(self) -> bool:
        return self.usuario is not None
