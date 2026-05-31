"""
vista/oferta_vista.py
Vista de gestión de Ofertas de Prácticas.
"""

from PyQt6.QtWidgets import QPushButton
from modelo.entidades import EstadoOferta
from .widgets import (
    SeccionBase, DialogoBase, BTN_WARNING, BTN_SUCCESS,
    confirmar_eliminacion, msg_error, msg_ok, msg_warn
)


class DialogoOferta(DialogoBase):
    def __init__(self, empresas: list, oferta=None, parent=None):
        titulo = "Nueva Oferta de Práctica" if not oferta else "Editar Oferta"
        super().__init__(titulo, parent)
        self.setMinimumWidth(520)

        self.cmb_empresa = self._campo_combo(
            [(e.nombre, e.id_empresa) for e in empresas]
        )
        self.txt_desc    = self._campo_area("Describe el puesto o área de práctica…", 80)
        self.txt_req     = self._campo_area("Requisitos del estudiante…", 70)
        self.cmb_estado  = self._campo_combo(EstadoOferta.TODOS)

        self._agregar_campo("Empresa *",     self.cmb_empresa, True)
        self._agregar_campo("Descripción *", self.txt_desc,    True)
        self._agregar_campo("Requisitos",    self.txt_req)
        self._agregar_campo("Estado",        self.cmb_estado)

        if oferta:
            idx = self.cmb_empresa.findData(oferta.id_empresa)
            if idx >= 0: self.cmb_empresa.setCurrentIndex(idx)
            self.txt_desc.setPlainText(oferta.descripcion)
            self.txt_req.setPlainText(oferta.requisitos)
            idx2 = self.cmb_estado.findText(oferta.estado)
            if idx2 >= 0: self.cmb_estado.setCurrentIndex(idx2)

    def datos(self):
        return (
            self.cmb_empresa.currentData(),
            self.txt_desc.toPlainText(),
            self.txt_req.toPlainText(),
            self.cmb_estado.currentText(),
        )


class OfertaVista(SeccionBase):
    def __init__(self, ctrl_oferta, ctrl_empresa, parent=None):
        self.ctrl  = ctrl_oferta
        self.ctrlE = ctrl_empresa
        super().__init__("📋  Ofertas de Práctica", parent)

    def _headers(self):
        return ["ID", "Empresa", "Descripción", "Estado", "Postulaciones"]

    def _botones_extra(self):
        self.btn_cerrar = QPushButton("🔒  Cerrar Oferta")
        self.btn_activar = QPushButton("✅  Activar")
        self.btn_cerrar.setEnabled(False)
        self.btn_activar.setEnabled(False)
        return [(self.btn_cerrar, BTN_WARNING), (self.btn_activar, BTN_SUCCESS)]

    def _setup_base(self):
        super()._setup_base()
        self.btn_cerrar.clicked.connect(self._cerrar_sel)
        self.btn_activar.clicked.connect(self._activar_sel)
        self._tabla.itemSelectionChanged.connect(self._sync_botones)

    def _sync_botones(self):
        id_ = self._tabla.id_sel()
        tiene = id_ is not None
        self.btn_cerrar.setEnabled(tiene)
        self.btn_activar.setEnabled(tiene)

    def _cargar_filas(self):
        from modelo.repositorio import Repositorio
        repo = Repositorio()
        filas = []
        for o in self.ctrl.listar():
            emp = self.ctrlE.obtener(o.id_empresa)
            n_posts = len(repo.postulaciones_oferta(o.id_oferta))
            filas.append([
                o.id_oferta,
                emp.nombre if emp else o.id_empresa,
                o.descripcion[:60] + ("…" if len(o.descripcion) > 60 else ""),
                o.estado,
                n_posts,
            ])
        return filas

    def _on_agregar(self):
        empresas = self.ctrlE.listar()
        if not empresas:
            msg_warn(self, "Primero registre al menos una empresa.")
            return
        dlg = DialogoOferta(empresas, parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            id_emp, desc, req, estado = dlg.datos()
            ok, msg = self.ctrl.agregar(id_emp, desc, req)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_editar(self, id_):
        o = self.ctrl.obtener(id_)
        dlg = DialogoOferta(self.ctrlE.listar(), oferta=o, parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            id_emp, desc, req, estado = dlg.datos()
            ok, msg = self.ctrl.actualizar(id_, id_emp, desc, req, estado)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_eliminar(self, id_):
        if confirmar_eliminacion(self, "esta oferta"):
            ok, msg = self.ctrl.eliminar(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _cerrar_sel(self):
        id_ = self._tabla.id_sel()
        if id_:
            ok, msg = self.ctrl.cambiar_estado(id_, EstadoOferta.CERRADA)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _activar_sel(self):
        id_ = self._tabla.id_sel()
        if id_:
            ok, msg = self.ctrl.cambiar_estado(id_, EstadoOferta.ACTIVA)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()
