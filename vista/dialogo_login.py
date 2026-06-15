"""
vista/dialogo_login.py
Diálogo de inicio de sesión. Autentica contra ControladorUsuario; si tiene éxito
expone el Usuario autenticado vía usuario(). Si el usuario cancela, el diálogo se
rechaza y la aplicación termina.
"""

from PyQt6.QtWidgets import QLineEdit, QLabel, QDialogButtonBox

from vista.widgets import DialogoBase, BTN_PRIMARY, BTN_SECONDARY, msg_error, msg_ok
from modelo.rol_usuario import RolUsuario


class DialogoLogin(DialogoBase):
    def __init__(self, ctrl_usuario, parent=None):
        super().__init__("Iniciar sesión", parent)
        self.ctrl = ctrl_usuario
        self._usuario = None

        self.txt_usuario = self._campo_texto("usuario")
        self.txt_pass = self._campo_texto("contraseña")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self._agregar_campo("Usuario", self.txt_usuario, required=True)
        self._agregar_campo("Contraseña", self.txt_pass, required=True)

    def _build_buttons(self):
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Ingresar")
        btns.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(BTN_PRIMARY)
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet(BTN_SECONDARY)
        btns.accepted.connect(self._aceptar)
        btns.rejected.connect(self.reject)
        self._layout.addWidget(btns)

    def _aceptar(self):
        u = self.ctrl.autenticar(self.txt_usuario.text(), self.txt_pass.text())
        if u is None:
            msg_error(self, "Usuario o contraseña incorrectos.")
            return
        self._usuario = u
        self.accept()

    def usuario(self):
        return self._usuario


class DialogoPrimerAdmin(DialogoBase):
    """Configuración inicial: cuando la base no tiene usuarios, crea el administrador.

    Se muestra una sola vez (primer arranque o tras borrar el archivo de datos).
    No se siembran datos de ejemplo: el sistema queda vacío salvo este administrador.
    """

    def __init__(self, ctrl_usuario, parent=None):
        super().__init__("Configuración inicial", parent)
        self.ctrl = ctrl_usuario

        info = QLabel("No hay usuarios registrados. Cree la cuenta de administrador "
                      "para comenzar a usar el sistema.")
        info.setWordWrap(True)
        info.setStyleSheet("color:#555;")
        self._form.addRow(info)

        self.txt_nombre = self._campo_texto("nombre de usuario")
        self.txt_pass = self._campo_texto("contraseña")
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_pass2 = self._campo_texto("repita la contraseña")
        self.txt_pass2.setEchoMode(QLineEdit.EchoMode.Password)
        self._agregar_campo("Usuario", self.txt_nombre, required=True)
        self._agregar_campo("Contraseña", self.txt_pass, required=True)
        self._agregar_campo("Confirmar", self.txt_pass2, required=True)

    def _build_buttons(self):
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Crear administrador")
        btns.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(BTN_PRIMARY)
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Salir")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet(BTN_SECONDARY)
        btns.accepted.connect(self._aceptar)
        btns.rejected.connect(self.reject)
        self._layout.addWidget(btns)

    def _aceptar(self):
        if self.txt_pass.text() != self.txt_pass2.text():
            msg_error(self, "Las contraseñas no coinciden.")
            return
        ok, msg = self.ctrl.agregar(
            self.txt_nombre.text(), self.txt_pass.text(),
            RolUsuario.ADMINISTRADOR, None,
        )
        if not ok:
            msg_error(self, msg)
            return
        msg_ok(self, "Administrador creado. Ahora inicie sesión.")
        self.accept()
