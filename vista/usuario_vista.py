"""
vista/usuario_vista.py
Gestión de Usuarios del sistema (solo Administrador).
Permite crear/editar/eliminar usuarios y vincularlos a su entidad según el rol.
"""

from PyQt6.QtWidgets import QLabel

from .widgets import (
    SeccionBase, DialogoBase,
    confirmar_eliminacion, msg_error, msg_ok,
)

from modelo import permisos
from modelo.rol_usuario import RolUsuario
from modelo.sesion import Sesion
from modelo.repositorio import Repositorio


def _nombre_entidad(ent, fallback):
    if ent is None:
        return fallback
    return getattr(ent, "nombre_completo", None) or getattr(ent, "nombre", fallback)


class DialogoUsuario(DialogoBase):
    def __init__(self, usuario=None, parent=None):
        super().__init__("Crear Usuario" if not usuario else "Editar Usuario", parent)
        self.setMinimumWidth(500)

        self.txt_nombre = self._campo_texto("nombre de usuario")
        self.txt_pass   = self._campo_texto("contraseña")
        self.cmb_rol    = self._campo_combo(RolUsuario.TODOS)
        self.cmb_ref    = self._campo_combo([])   # se llena según el rol

        self._agregar_campo("Usuario *",    self.txt_nombre, True)
        self._agregar_campo("Contraseña *", self.txt_pass,   True)
        self._agregar_campo("Rol *",        self.cmb_rol,    True)
        self._agregar_campo("Vinculado a",  self.cmb_ref)

        # Al cambiar el rol, repoblar la lista de entidades vinculables
        self.cmb_rol.currentTextChanged.connect(self._poblar_ref)
        self._poblar_ref(self.cmb_rol.currentText())

        if usuario:
            self.txt_nombre.setText(usuario.nombre)
            self.txt_pass.setText(usuario.password)
            i = self.cmb_rol.findText(usuario.rol)
            if i >= 0:
                self.cmb_rol.setCurrentIndex(i)
            self._poblar_ref(usuario.rol)
            if usuario.ref_id:
                j = self.cmb_ref.findData(usuario.ref_id)
                if j >= 0:
                    self.cmb_ref.setCurrentIndex(j)

    def _poblar_ref(self, rol):
        repo = Repositorio()
        self.cmb_ref.clear()
        if rol == RolUsuario.ADMINISTRADOR:
            self.cmb_ref.addItem("— (no aplica) —", None)
            self.cmb_ref.setEnabled(False)
            return
        self.cmb_ref.setEnabled(True)
        # El vínculo es opcional: siempre se puede crear el usuario "sin vincular"
        # (útil cuando aún no existe la entidad; se puede vincular luego al editar).
        self.cmb_ref.addItem("— Sin vincular —", None)
        if rol == RolUsuario.COORDINADOR:
            items = [(c.nombre_completo, c.id_coordinador) for c in repo.listar_coordinadores()]
        elif rol == RolUsuario.EMPRESA:
            items = [(e.nombre, e.id_empresa) for e in repo.listar_empresas()]
        elif rol == RolUsuario.TUTOR:
            items = [(t.nombre_completo, t.id_tutor) for t in repo.listar_t_academicos()]
        elif rol == RolUsuario.ESTUDIANTE:
            items = [(e.nombre_completo, e.id_estudiante) for e in repo.listar_estudiantes()]
        else:
            items = []
        for texto, data in items:
            self.cmb_ref.addItem(texto, data)

    def datos(self):
        return (self.txt_nombre.text(), self.txt_pass.text(),
                self.cmb_rol.currentText(), self.cmb_ref.currentData())


class UsuarioVista(SeccionBase):
    def __init__(self, ctrl_usuario, parent=None):
        self.ctrl = ctrl_usuario
        super().__init__("👤  Usuarios", parent, seccion_idx=permisos.USUARIOS)

    def _setup_base(self):
        super()._setup_base()
        nota = QLabel(
            "ℹ  Para un usuario de rol Empresa, Estudiante, Tutor o Coordinador, primero "
            "registre esa entidad en su sección (Empresas, Estudiantes, Tutores, "
            "Coordinadores) y luego selecciónela en «Vinculado a». También puede crear el "
            "usuario «Sin vincular» y asociarlo después con Editar."
        )
        nota.setWordWrap(True)
        nota.setStyleSheet(
            "background:#E3F2FD; color:#0D3166; border:1px solid #90CAF9; "
            "border-radius:6px; padding:10px 12px;"
        )
        self.layout().insertWidget(2, nota)

    def _headers(self):
        return ["ID", "Usuario", "Rol", "Vinculado a"]

    def _cargar_filas(self):
        repo = Repositorio()
        getters = {
            RolUsuario.COORDINADOR: repo.obtener_coordinador,
            RolUsuario.EMPRESA:     repo.obtener_empresa,
            RolUsuario.TUTOR:       repo.obtener_t_academico,
            RolUsuario.ESTUDIANTE:  repo.obtener_estudiante,
        }
        filas = []
        for u in self.ctrl.listar():
            if not u.ref_id:
                vinculo = "—"
            else:
                g = getters.get(u.rol)
                vinculo = _nombre_entidad(g(u.ref_id) if g else None, u.ref_id)
            filas.append([u.id_usuario, u.nombre, u.rol, vinculo])
        return filas

    def _on_agregar(self):
        dlg = DialogoUsuario(parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.agregar(*dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_editar(self, id_):
        u = self.ctrl.obtener(id_)
        if not u:
            return
        dlg = DialogoUsuario(usuario=u, parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.actualizar(id_, *dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_eliminar(self, id_):
        actual = Sesion().usuario
        if actual and actual.id_usuario == id_:
            msg_error(self, "No puede eliminar el usuario con el que inició sesión.")
            return
        if confirmar_eliminacion(self, "este usuario"):
            ok, msg = self.ctrl.eliminar(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()
