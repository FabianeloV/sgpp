"""
vista/tutor_vista.py
Vistas para Tutores Académicos, Tutores Empresariales y Coordinadores.
"""

from PyQt6.QtWidgets import QPushButton, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtGui import QFont

from .widgets import (
    SeccionBase, DialogoBase, BTN_PRIMARY,
    PRIMARY, BG,
    confirmar_eliminacion, msg_error, msg_ok,
)

from modelo import permisos
from modelo.rol_usuario import RolUsuario
from modelo.sesion import Sesion
from modelo.repositorio import Repositorio


# ── Diálogos ──────────────────────────────────────────────────────────────────

class DialogoTutorAcademico(DialogoBase):
    def __init__(self, tutor=None, parent=None):
        super().__init__("Registrar Tutor Académico" if not tutor else "Editar Tutor Académico",
                         parent)
        self.txt_nombre   = self._campo_texto("Nombre")
        self.txt_apellido = self._campo_texto("Apellido")
        self.txt_correo   = self._campo_texto("correo@ucuenca.edu.ec")
        self.txt_tel      = self._campo_texto("09XXXXXXXX")
        self.txt_area     = self._campo_texto("Ej. Redes y Telecomunicaciones")

        self._agregar_campo("Nombre *",    self.txt_nombre,   True)
        self._agregar_campo("Apellido *",  self.txt_apellido, True)
        self._agregar_campo("Correo",      self.txt_correo)
        self._agregar_campo("Teléfono",    self.txt_tel)
        self._agregar_campo("Área",        self.txt_area)

        if tutor:
            self.txt_nombre.setText(tutor.nombre)
            self.txt_apellido.setText(tutor.apellido)
            self.txt_correo.setText(tutor.correo)
            self.txt_tel.setText(tutor.telefono)
            self.txt_area.setText(tutor.area)

    def datos(self):
        return (self.txt_nombre.text(), self.txt_apellido.text(),
                self.txt_correo.text(), self.txt_tel.text(),
                self.txt_area.text())


class DialogoTutorEmpresarial(DialogoBase):
    def __init__(self, tutor=None, parent=None, id_empresa_fijo=None):
        super().__init__("Registrar Tutor Empresarial" if not tutor else "Editar Tutor Empresarial",
                         parent)
        self.txt_nombre   = self._campo_texto("Nombre")
        self.txt_apellido = self._campo_texto("Apellido")
        self.txt_correo   = self._campo_texto("correo@empresa.com")
        self.txt_tel      = self._campo_texto("09XXXXXXXX")
        self.txt_cargo    = self._campo_texto("Ej. Jefe de TI")

        opciones = [(e.nombre, e.id_empresa) for e in Repositorio().listar_empresas()]
        self.cmb_empresa  = self._campo_combo(opciones)

        self._agregar_campo("Nombre *",    self.txt_nombre,   True)
        self._agregar_campo("Apellido *",  self.txt_apellido, True)
        self._agregar_campo("Correo",      self.txt_correo)
        self._agregar_campo("Teléfono",    self.txt_tel)
        self._agregar_campo("Cargo",       self.txt_cargo)
        self._agregar_campo("Empresa",     self.cmb_empresa)

        if tutor:
            self.txt_nombre.setText(tutor.nombre)
            self.txt_apellido.setText(tutor.apellido)
            self.txt_correo.setText(tutor.correo)
            self.txt_tel.setText(tutor.telefono)
            self.txt_cargo.setText(tutor.cargo)
            id_emp = getattr(tutor, "id_empresa", "")
            if id_emp:
                idx = self.cmb_empresa.findData(id_emp)
                if idx >= 0:
                    self.cmb_empresa.setCurrentIndex(idx)

        if id_empresa_fijo:
            idx = self.cmb_empresa.findData(id_empresa_fijo)
            if idx >= 0:
                self.cmb_empresa.setCurrentIndex(idx)
            self.cmb_empresa.setEnabled(False)

    def datos(self):
        return (self.txt_nombre.text(), self.txt_apellido.text(),
                self.txt_correo.text(), self.txt_tel.text(),
                self.txt_cargo.text(), self.cmb_empresa.currentData())


# ── Vistas CRUD ───────────────────────────────────────────────────────────────

class TutorAcademicoVista(SeccionBase):
    def __init__(self, ctrl, parent=None):
        self.ctrl = ctrl
        super().__init__("👨‍🏫  Tutores Académicos", parent)

    def _headers(self):
        return ["ID", "Nombre", "Apellido", "Correo", "Teléfono", "Área"]

    def _cargar_filas(self):
        return [
            [t.id_tutor, t.nombre, t.apellido, t.correo, t.telefono, t.area]
            for t in self.ctrl.listar_academicos()
        ]

    def _on_agregar(self):
        dlg = DialogoTutorAcademico(parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.agregar_academico(*dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_editar(self, id_):
        t = self.ctrl.repo.obtener_t_academico(id_)
        dlg = DialogoTutorAcademico(tutor=t, parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.actualizar_academico(id_, *dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_eliminar(self, id_):
        if confirmar_eliminacion(self, "este tutor académico"):
            ok, msg = self.ctrl.eliminar_academico(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()


class TutorEmpresarialVista(SeccionBase):
    def __init__(self, ctrl, parent=None):
        self.ctrl = ctrl
        super().__init__("🤝  Tutores Empresariales", parent, seccion_idx=permisos.TUTORES)

    def _headers(self):
        return ["ID", "Nombre", "Apellido", "Correo", "Teléfono", "Cargo"]

    def _cargar_filas(self):
        if self._es(RolUsuario.EMPRESA):
            tutores = Repositorio().tutores_empresariales_empresa(self._ref_id())
        else:
            tutores = self.ctrl.listar_empresariales()
        return [
            [t.id_tutor, t.nombre, t.apellido, t.correo, t.telefono, t.cargo]
            for t in tutores
        ]

    def _on_agregar(self):
        id_fijo = self._ref_id() if self._es(RolUsuario.EMPRESA) else None
        dlg = DialogoTutorEmpresarial(parent=self, id_empresa_fijo=id_fijo)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.agregar_empresarial(*dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_editar(self, id_):
        t = self.ctrl.repo.obtener_t_empresarial(id_)
        if self._es(RolUsuario.EMPRESA) and getattr(t, "id_empresa", "") != self._ref_id():
            msg_error(self, "No tiene permiso para editar este tutor empresarial.")
            return
        id_fijo = self._ref_id() if self._es(RolUsuario.EMPRESA) else None
        dlg = DialogoTutorEmpresarial(tutor=t, parent=self, id_empresa_fijo=id_fijo)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.actualizar_empresarial(id_, *dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_eliminar(self, id_):
        if self._es(RolUsuario.EMPRESA):
            t = self.ctrl.repo.obtener_t_empresarial(id_)
            if not t or getattr(t, "id_empresa", "") != self._ref_id():
                msg_error(self, "No tiene permiso para eliminar este tutor empresarial.")
                return
        if confirmar_eliminacion(self, "este tutor empresarial"):
            ok, msg = self.ctrl.eliminar_empresarial(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()


# ── Vista combinada con pestañas ──────────────────────────────────────────────

class TutorVista(QWidget):
    """Contenedor con tabs para Tutor Académico y Tutor Empresarial."""

    def __init__(self, ctrl_tutor, parent=None):
        super().__init__(parent)
        self.ctrl = ctrl_tutor
        self.setStyleSheet(f"background:{BG};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab {
                padding: 8px 20px; font-weight:normal;
            }
            QTabBar::tab:selected { color: #1B4F8A; border-bottom: 2px solid #1B4F8A; }
        """)

        self.vista_ac = None
        self.vista_em = TutorEmpresarialVista(ctrl_tutor)

        # Empresa solo gestiona tutores empresariales: sin pestaña de académicos.
        if Sesion().rol != RolUsuario.EMPRESA:
            self.vista_ac = TutorAcademicoVista(ctrl_tutor)
            tabs.addTab(self.vista_ac, "👨‍🏫  Tutores Académicos")
        tabs.addTab(self.vista_em, "🤝  Tutores Empresariales")
        lay.addWidget(tabs)

    def actualizar(self):
        if self.vista_ac is not None:
            self.vista_ac.actualizar()
        self.vista_em.actualizar()


# ── Vista Coordinador ─────────────────────────────────────────────────────────

class DialogoCoordinador(DialogoBase):
    def __init__(self, coordinador=None, parent=None):
        super().__init__("Registrar Coordinador" if not coordinador else "Editar Coordinador",
                         parent)
        self.txt_nombre   = self._campo_texto("Nombre")
        self.txt_apellido = self._campo_texto("Apellido")
        self.txt_correo   = self._campo_texto("correo@ucuenca.edu.ec")
        self.txt_tel      = self._campo_texto("09XXXXXXXX")
        self.txt_cedula   = self._campo_texto("0100000000")

        self._agregar_campo("Nombre *",    self.txt_nombre,   True)
        self._agregar_campo("Apellido *",  self.txt_apellido, True)
        self._agregar_campo("Correo",      self.txt_correo)
        self._agregar_campo("Teléfono",    self.txt_tel)
        self._agregar_campo("Cédula *",    self.txt_cedula,   True)

        if coordinador:
            self.txt_nombre.setText(coordinador.nombre)
            self.txt_apellido.setText(coordinador.apellido)
            self.txt_correo.setText(coordinador.correo)
            self.txt_tel.setText(coordinador.telefono)
            self.txt_cedula.setText(coordinador.cedula)

    def datos(self):
        return (self.txt_nombre.text(), self.txt_apellido.text(),
                self.txt_correo.text(), self.txt_tel.text(),
                self.txt_cedula.text())


class CoordinadorVista(SeccionBase):
    def __init__(self, ctrl, parent=None):
        self.ctrl = ctrl
        super().__init__("👔  Coordinadores de Vinculación", parent)

    def _headers(self):
        return ["ID", "Nombre", "Apellido", "Correo", "Teléfono", "Cédula"]

    def _cargar_filas(self):
        return [
            [c.id_coordinador, c.nombre, c.apellido, c.correo, c.telefono, c.cedula]
            for c in self.ctrl.listar()
        ]

    def _on_agregar(self):
        dlg = DialogoCoordinador(parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.agregar(*dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_editar(self, id_):
        c = self.ctrl.obtener(id_)
        dlg = DialogoCoordinador(coordinador=c, parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.actualizar(id_, *dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_eliminar(self, id_):
        if confirmar_eliminacion(self, "este coordinador"):
            ok, msg = self.ctrl.eliminar(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()
