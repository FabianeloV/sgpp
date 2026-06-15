"""
Controlador principal de la aplicación.

Centraliza el arranque: configuración inicial (creación del primer administrador
si la base está vacía), inicio de sesión y construcción de la ventana principal.
"""

import os
import sys

from modelo.repositorio import Repositorio
from modelo.sesion import Sesion

from controlador.controlador_usuario import ControladorUsuario


class ControladorPrincipal:
    def __init__(self, argv=None, directorio_proyecto: str | None = None):
        self.argv = argv or sys.argv
        self.directorio_proyecto = directorio_proyecto or os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
        self.repo = Repositorio()
        self.app = None
        self.ventana = None

    def ejecutar(self) -> int:
        os.chdir(self.directorio_proyecto)

        from PyQt6.QtGui import QFont
        from PyQt6.QtWidgets import QApplication, QDialog
        from vista.main_window import MainWindow
        from vista.dialogo_login import DialogoLogin, DialogoPrimerAdmin

        self.app = QApplication(self.argv)
        self.app.setApplicationName("SGPP")
        self.app.setOrganizationName("Universidad de Cuenca")

        fuente = QFont("Segoe UI", 10)
        fuente.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
        self.app.setFont(fuente)
        self.app.setStyleSheet(self._estilo_global())

        ctrl_usuario = ControladorUsuario()

        # Primer uso: si la base no tiene usuarios, pedir crear el administrador inicial.
        # El sistema NO siembra datos de demostración; arranca completamente vacío.
        if not ctrl_usuario.listar():
            if DialogoPrimerAdmin(ctrl_usuario).exec() != QDialog.DialogCode.Accepted:
                return 0                       # canceló la creación del admin -> salir

        # Bucle de sesión: login -> ventana principal -> (cerrar sesión) -> login
        while True:
            login = DialogoLogin(ctrl_usuario)
            if login.exec() != QDialog.DialogCode.Accepted:
                return 0                       # canceló el login -> salir
            Sesion().establecer(login.usuario())

            self.ventana = MainWindow()
            self.ventana.show()
            self.app.exec()

            if not self.ventana.relogin:
                return 0                       # cierre normal -> terminar
            Sesion().limpiar()                 # cerrar sesión -> volver al login

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
