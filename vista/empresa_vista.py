"""
vista/empresa_vista.py
Vistas para Empresa y Convenio.
"""

from PyQt6.QtWidgets import (
    QPushButton, QLabel, QDialog, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QWidget, QDialogButtonBox,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QFont

from .widgets import (
    SeccionBase, DialogoBase, Tabla, BTN_PRIMARY, BTN_SECONDARY,
    BTN_WARNING, PRIMARY, BORDER, SURFACE, BG,
    confirmar_eliminacion, msg_error, msg_ok
)


# ── Diálogos ──────────────────────────────────────────────────────────────────

class DialogoEmpresa(DialogoBase):
    def __init__(self, empresa=None, parent=None):
        super().__init__("Registrar Empresa" if not empresa else "Editar Empresa", parent)
        self.txt_nombre = self._campo_texto("Ej. Tecnología S.A.")
        self.txt_ruc    = self._campo_texto("1234567890001")
        self._agregar_campo("Nombre *", self.txt_nombre, True)
        self._agregar_campo("RUC *",    self.txt_ruc,    True)
        if empresa:
            self.txt_nombre.setText(empresa.nombre)
            self.txt_ruc.setText(empresa.RUC)

    def datos(self):
        return self.txt_nombre.text(), self.txt_ruc.text()


class DialogoConvenio(DialogoBase):
    def __init__(self, empresas: list, convenio=None, parent=None):
        super().__init__("Registrar Convenio" if not convenio else "Editar Convenio", parent)
        self.cmb_empresa = self._campo_combo(
            [(e.nombre, e.id_empresa) for e in empresas]
        )
        self.fecha_inicio = self._campo_fecha()
        self.fecha_fin    = self._campo_fecha()
        self._agregar_campo("Empresa *",      self.cmb_empresa,  True)
        self._agregar_campo("Fecha Inicio *", self.fecha_inicio, True)
        self._agregar_campo("Fecha Fin *",    self.fecha_fin,    True)
        if convenio:
            idx = self.cmb_empresa.findData(convenio.id_empresa)
            if idx >= 0: self.cmb_empresa.setCurrentIndex(idx)
            fi = convenio.fecha_inicio.split("-")
            self.fecha_inicio.setDate(QDate(int(fi[0]), int(fi[1]), int(fi[2])))
            ff = convenio.fecha_fin.split("-")
            self.fecha_fin.setDate(QDate(int(ff[0]), int(ff[1]), int(ff[2])))

    def datos(self):
        return (
            self.cmb_empresa.currentData(),
            self.fecha_inicio.date().toString("yyyy-MM-dd"),
            self.fecha_fin.date().toString("yyyy-MM-dd"),
        )


# ── Vista Empresa ─────────────────────────────────────────────────────────────

class EmpresaVista(SeccionBase):
    def __init__(self, ctrl_empresa, ctrl_convenio, parent=None):
        self.ctrl  = ctrl_empresa
        self.ctrlC = ctrl_convenio
        super().__init__("🏢  Empresas", parent)

    def _headers(self):
        return ["ID", "Nombre", "RUC", "Convenio Vigente", "Ofertas"]

    def _botones_extra(self):
        self.btn_convenios = QPushButton("📋  Convenios")
        return [(self.btn_convenios, BTN_WARNING)]

    def _setup_base(self):
        super()._setup_base()
        self.btn_convenios.clicked.connect(self._ver_convenios)
        self._tabla.itemSelectionChanged.connect(
            lambda: self.btn_convenios.setEnabled(self._tabla.id_sel() is not None)
        )
        self.btn_convenios.setEnabled(False)

    def _cargar_filas(self):
        from modelo.repositorio import Repositorio
        repo = Repositorio()
        filas = []
        for e in self.ctrl.listar():
            vigente = "✔ Sí" if self.ctrlC.tiene_vigente(e.id_empresa) else "✗ No"
            nofertas = len(repo.ofertas_empresa(e.id_empresa))
            filas.append([e.id_empresa, e.nombre, e.RUC, vigente, nofertas])
        return filas

    def _on_agregar(self):
        dlg = DialogoEmpresa(parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.agregar(*dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_editar(self, id_):
        e = self.ctrl.obtener(id_)
        dlg = DialogoEmpresa(empresa=e, parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.actualizar(id_, *dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_eliminar(self, id_):
        e = self.ctrl.obtener(id_)
        if e and confirmar_eliminacion(self, f"la empresa '{e.nombre}'"):
            ok, msg = self.ctrl.eliminar(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _ver_convenios(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        e = self.ctrl.obtener(id_)
        dlg = _DialogoConveniosSub(e, self.ctrlC, parent=self)
        dlg.exec()
        self.actualizar()


class _DialogoConveniosSub(QDialog):
    """Sub-ventana para gestionar convenios de una empresa."""

    def __init__(self, empresa, ctrl_convenio, parent=None):
        super().__init__(parent)
        self.emp  = empresa
        self.ctrl = ctrl_convenio
        self.setWindowTitle(f"Convenios – {empresa.nombre}")
        self.setMinimumSize(620, 400)
        self.setStyleSheet(f"background:{SURFACE};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        lbl = QLabel(f"Convenios de <b>{empresa.nombre}</b>")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lay.addWidget(lbl)

        bar = QHBoxLayout()
        self.btn_add = QPushButton("＋ Nuevo Convenio")
        self.btn_del = QPushButton("✕ Eliminar")
        self.btn_add.setStyleSheet(BTN_PRIMARY)
        self.btn_del.setStyleSheet(from_import())
        bar.addWidget(self.btn_add); bar.addWidget(self.btn_del); bar.addStretch()
        lay.addLayout(bar)

        self.tabla = Tabla(["ID", "Fecha Inicio", "Fecha Fin", "Estado"])
        lay.addWidget(self.tabla)

        self.btn_add.clicked.connect(self._agregar)
        self.btn_del.clicked.connect(self._eliminar)
        self.tabla.itemSelectionChanged.connect(
            lambda: self.btn_del.setEnabled(self.tabla.id_sel() is not None)
        )
        self.btn_del.setEnabled(False)
        self._cargar()

    def _cargar(self):
        convs = self.ctrl.de_empresa(self.emp.id_empresa)
        self.tabla.llenar([
            [c.id_convenio, c.fecha_inicio, c.fecha_fin, c.estado_str]
            for c in convs
        ])

    def _agregar(self):
        from modelo.repositorio import Repositorio
        dlg = DialogoConvenio([self.emp], parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            ok, msg = self.ctrl.agregar(*dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self._cargar()

    def _eliminar(self):
        id_ = self.tabla.id_sel()
        if id_ and confirmar_eliminacion(self, "este convenio"):
            ok, msg = self.ctrl.eliminar(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self._cargar()


def from_import():
    """Import helper to avoid circular issue."""
    from .widgets import BTN_DANGER
    return BTN_DANGER
