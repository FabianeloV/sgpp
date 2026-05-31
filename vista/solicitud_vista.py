"""
vista/solicitud_vista.py
Vista de Solicitudes de Autorización (por empresa propia, oficios, certificados).
"""

from PyQt6.QtWidgets import QPushButton
from modelo.entidades import TipoSolicitud, EstadoSolicitud
from .widgets import (
    SeccionBase, DialogoBase,
    BTN_SUCCESS, BTN_DANGER,
    confirmar_eliminacion, msg_error, msg_ok, msg_warn,
)


class DialogoSolicitud(DialogoBase):
    def __init__(self, estudiantes: list, empresas: list, parent=None):
        super().__init__("Nueva Solicitud", parent)

        self.cmb_est   = self._campo_combo(
            [(f"{e.nombre_completo} (ciclo {e.ciclo})", e.id_estudiante) for e in estudiantes]
        )
        self.cmb_tipo  = self._campo_combo(TipoSolicitud.TODOS)
        self.cmb_emp   = self._campo_combo(
            [("— Sin empresa —", "")] + [(e.nombre, e.id_empresa) for e in empresas]
        )

        self._agregar_campo("Estudiante *", self.cmb_est,  True)
        self._agregar_campo("Tipo *",       self.cmb_tipo, True)
        self._agregar_campo("Empresa",      self.cmb_emp)

    def datos(self):
        id_emp = self.cmb_emp.currentData() or None
        return self.cmb_est.currentData(), self.cmb_tipo.currentText(), id_emp


class DialogoResolver(DialogoBase):
    def __init__(self, coordinadores: list, parent=None):
        super().__init__("Resolver Solicitud", parent)
        self.cmb_estado = self._campo_combo(
            [EstadoSolicitud.APROBADA, EstadoSolicitud.RECHAZADA]
        )
        self.cmb_coord = self._campo_combo(
            [(c.nombre_completo, c.id_coordinador) for c in coordinadores]
        )
        self.txt_obs = self._campo_area("Observaciones o motivo…", 60)

        self._agregar_campo("Resolución *",    self.cmb_estado, True)
        self._agregar_campo("Coordinador *",   self.cmb_coord,  True)
        self._agregar_campo("Observaciones",   self.txt_obs)

    def datos(self):
        return (
            self.cmb_estado.currentText(),
            self.cmb_coord.currentData(),
            self.txt_obs.toPlainText(),
        )


class SolicitudVista(SeccionBase):
    def __init__(self, ctrl_sol, ctrl_est, ctrl_emp, ctrl_coord, parent=None):
        self.ctrl  = ctrl_sol
        self.ctrlE = ctrl_est
        self.ctrlEmp = ctrl_emp
        self.ctrlC = ctrl_coord
        super().__init__("📩  Solicitudes de Autorización", parent)

    def _headers(self):
        return ["ID", "Estudiante", "Tipo", "Empresa", "Fecha", "Estado", "Coordinador"]

    def _botones_extra(self):
        self.btn_resolver = QPushButton("⚖  Resolver")
        self.btn_resolver.setEnabled(False)
        return [(self.btn_resolver, BTN_SUCCESS)]

    def _setup_base(self):
        super()._setup_base()
        self.btn_resolver.clicked.connect(self._resolver_sel)
        self._tabla.itemSelectionChanged.connect(self._sync_botones)

    def _sync_botones(self):
        id_ = self._tabla.id_sel()
        tiene = id_ is not None
        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(tiene)
        if tiene:
            s = self.ctrl.obtener(id_)
            self.btn_resolver.setEnabled(
                s is not None and s.estado == EstadoSolicitud.PENDIENTE
            )
        else:
            self.btn_resolver.setEnabled(False)

    def _cargar_filas(self):
        filas = []
        for s in self.ctrl.listar():
            est   = self.ctrlE.obtener(s.id_estudiante)
            emp   = self.ctrlEmp.obtener(s.id_empresa) if s.id_empresa else None
            coord = self.ctrlC.obtener(s.id_coordinador) if s.id_coordinador else None
            filas.append([
                s.id_solicitud,
                est.nombre_completo if est else s.id_estudiante,
                s.tipo,
                emp.nombre if emp else "—",
                s.fecha,
                s.estado,
                coord.nombre_completo if coord else "—",
            ])
        return filas

    def actualizar(self):
        super().actualizar()
        from PyQt6.QtGui import QBrush, QColor
        colores = {
            EstadoSolicitud.PENDIENTE: "#FFFDE7",
            EstadoSolicitud.APROBADA:  "#E8F5E9",
            EstadoSolicitud.RECHAZADA: "#FFEBEE",
        }
        for row in range(self._tabla.rowCount()):
            item = self._tabla.item(row, 5)
            if item:
                c = colores.get(item.text(), "#FFF")
                b = QBrush(QColor(c))
                for col in range(self._tabla.columnCount()):
                    i = self._tabla.item(row, col)
                    if i: i.setBackground(b)

    def _on_agregar(self):
        ests   = self.ctrlE.listar()
        emps   = self.ctrlEmp.listar()
        if not ests:
            msg_warn(self, "Registre estudiantes primero.")
            return
        dlg = DialogoSolicitud(ests, emps, parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.agregar(*dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_editar(self, id_): pass

    def _on_eliminar(self, id_):
        if confirmar_eliminacion(self, "esta solicitud"):
            ok, msg = self.ctrl.eliminar(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _resolver_sel(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        coords = self.ctrlC.listar()
        if not coords:
            msg_warn(self, "Registre al menos un coordinador primero.")
            return
        dlg = DialogoResolver(coords, parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.resolver(id_, *dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()
