"""
vista/postulacion_vista.py
Vistas para Postulación y Terna.
"""

from PyQt6.QtWidgets import (
    QPushButton, QLabel, QDialog, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QFrame, QTextEdit, QDialogButtonBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush

from modelo.entidades import EstadoPostulacion, EstadoTerna
from .widgets import (
    SeccionBase, DialogoBase, Tabla,
    BTN_PRIMARY, BTN_SUCCESS, BTN_WARNING, BTN_DANGER, BTN_SECONDARY,
    PRIMARY, BORDER, SURFACE, BG,
    confirmar_eliminacion, msg_error, msg_ok, msg_warn,
    FORM_FIELD,
)


# ── Diálogo de nueva postulación ──────────────────────────────────────────────

class DialogoPostulacion(DialogoBase):
    def __init__(self, estudiantes: list, ofertas: list, coordinadores: list,
                 postulacion=None, parent=None):
        super().__init__("Nueva Postulación" if not postulacion else "Editar Postulación", parent)

        self.cmb_est  = self._campo_combo(
            [(f"{e.nombre_completo} (ciclo {e.ciclo})", e.id_estudiante) for e in estudiantes]
        )
        self.cmb_of   = self._campo_combo(
            [(o.descripcion[:50], o.id_oferta) for o in ofertas]
        )
        self.cmb_coord= self._campo_combo(
            [("— Sin asignar —", "")] +
            [(c.nombre_completo, c.id_coordinador) for c in coordinadores]
        )

        self._agregar_campo("Estudiante *",   self.cmb_est,   True)
        self._agregar_campo("Oferta *",        self.cmb_of,    True)
        self._agregar_campo("Coordinador",     self.cmb_coord)

        if postulacion:
            self._set_combo(self.cmb_est,   postulacion.id_estudiante)
            self._set_combo(self.cmb_of,    postulacion.id_oferta)
            self._set_combo(self.cmb_coord, postulacion.id_coordinador or "")

    def _set_combo(self, combo, valor):
        idx = combo.findData(valor)
        if idx >= 0: combo.setCurrentIndex(idx)

    def datos(self):
        coord = self.cmb_coord.currentData() or None
        return self.cmb_est.currentData(), self.cmb_of.currentData(), coord


# ── Diálogo de rechazo ────────────────────────────────────────────────────────

class DialogoRechazo(DialogoBase):
    def __init__(self, parent=None):
        super().__init__("Rechazar Postulación", parent)
        self.txt_obs = self._campo_area("Motivo del rechazo…")
        self._agregar_campo("Observaciones", self.txt_obs)

    def datos(self): return self.txt_obs.toPlainText()


# ── Vista Postulación ─────────────────────────────────────────────────────────

class PostulacionVista(SeccionBase):
    def __init__(self, ctrl_post, ctrl_est, ctrl_oferta, ctrl_coord, parent=None):
        self.ctrl  = ctrl_post
        self.ctrlE = ctrl_est
        self.ctrlO = ctrl_oferta
        self.ctrlC = ctrl_coord
        super().__init__("📝  Postulaciones", parent)

    def _headers(self):
        return ["ID", "Estudiante", "Oferta", "Fecha", "Estado", "Coordinador"]

    def _botones_extra(self):
        self.btn_validar  = QPushButton("✔  Validar")
        self.btn_rechazar = QPushButton("✗  Rechazar")
        self.btn_terna    = QPushButton("👥  A Terna")
        self.btn_aceptar  = QPushButton("🏆  Aceptar")
        for b in [self.btn_validar, self.btn_rechazar, self.btn_terna, self.btn_aceptar]:
            b.setEnabled(False)
        return [
            (self.btn_validar,  BTN_SUCCESS),
            (self.btn_rechazar, BTN_DANGER),
            (self.btn_terna,    BTN_WARNING),
            (self.btn_aceptar,  BTN_PRIMARY),
        ]

    def _setup_base(self):
        super()._setup_base()
        self.btn_validar.clicked.connect(self._validar_sel)
        self.btn_rechazar.clicked.connect(self._rechazar_sel)
        self.btn_terna.clicked.connect(self._agregar_terna_sel)
        self.btn_aceptar.clicked.connect(self._aceptar_sel)
        self._tabla.itemSelectionChanged.connect(self._sync_botones)
        # Eliminar no aplica si hay práctica, el ctrl ya lo valida
        self.btn_eliminar.setText("✕  Eliminar")

    def _sync_botones(self):
        id_ = self._tabla.id_sel()
        if not id_:
            for b in [self.btn_validar, self.btn_rechazar,
                      self.btn_terna, self.btn_aceptar,
                      self.btn_editar, self.btn_eliminar]:
                b.setEnabled(False)
            return
        post = self.ctrl.obtener(id_)
        if not post: return
        s = post.estado
        self.btn_validar.setEnabled(s == EstadoPostulacion.PENDIENTE)
        self.btn_rechazar.setEnabled(s in [EstadoPostulacion.PENDIENTE, EstadoPostulacion.VALIDADA])
        self.btn_terna.setEnabled(s == EstadoPostulacion.VALIDADA)
        self.btn_aceptar.setEnabled(s == EstadoPostulacion.EN_TERNA)
        self.btn_editar.setEnabled(s == EstadoPostulacion.PENDIENTE)
        self.btn_eliminar.setEnabled(True)

    def _cargar_filas(self):
        filas = []
        for p in self.ctrl.listar():
            est   = self.ctrlE.obtener(p.id_estudiante)
            of    = self.ctrlO.obtener(p.id_oferta)
            coord = self.ctrlC.obtener(p.id_coordinador) if p.id_coordinador else None
            filas.append([
                p.id_postulacion,
                est.nombre_completo if est else p.id_estudiante,
                of.descripcion[:45] + "…" if of and len(of.descripcion) > 45 else (of.descripcion if of else p.id_oferta),
                p.fecha,
                p.estado,
                coord.nombre_completo if coord else "—",
            ])
        return filas

    def _after_llenar(self):
        """Colorear filas por estado."""
        colores = {
            EstadoPostulacion.PENDIENTE:  "#FFFDE7",
            EstadoPostulacion.VALIDADA:   "#E8F5E9",
            EstadoPostulacion.EN_TERNA:   "#E3F2FD",
            EstadoPostulacion.ACEPTADA:   "#F3E5F5",
            EstadoPostulacion.RECHAZADA:  "#FFEBEE",
        }
        for row in range(self._tabla.rowCount()):
            item = self._tabla.item(row, 4)
            if item:
                color = colores.get(item.text(), "#FFFFFF")
                from PyQt6.QtGui import QBrush, QColor
                b = QBrush(QColor(color))
                for c in range(self._tabla.columnCount()):
                    i = self._tabla.item(row, c)
                    if i: i.setBackground(b)

    def actualizar(self):
        super().actualizar()
        self._after_llenar()

    def _on_agregar(self):
        ests   = [e for e in self.ctrlE.listar() if e.puede_practicas_externas()]
        ofertas= [o for o in self.ctrlO.listar() if o.estado == "Activa"]
        coords = self.ctrlC.listar()
        if not ests:
            msg_warn(self, "No hay estudiantes desde 6.° ciclo registrados.")
            return
        if not ofertas:
            msg_warn(self, "No hay ofertas activas disponibles.")
            return
        dlg = DialogoPostulacion(ests, ofertas, coords, parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.agregar(*dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_editar(self, id_):
        p = self.ctrl.obtener(id_)
        dlg = DialogoPostulacion(
            self.ctrlE.listar(), self.ctrlO.listar(),
            self.ctrlC.listar(), postulacion=p, parent=self
        )
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            # Reemplazar: eliminar y crear de nuevo sólo si pendiente
            est_id, of_id, coord_id = dlg.datos()
            from modelo.repositorio import Repositorio
            repo = Repositorio()
            post = repo.obtener_postulacion(id_)
            if post:
                post.id_estudiante = est_id
                post.id_oferta     = of_id
                post.id_coordinador= coord_id
                repo.actualizar_postulacion(post)
                msg_ok(self, "Postulación actualizada.")
                self.actualizar()

    def _on_eliminar(self, id_):
        if confirmar_eliminacion(self, "esta postulación"):
            ok, msg = self.ctrl.eliminar(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _validar_sel(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        coords = self.ctrlC.listar()
        if not coords:
            msg_warn(self, "Registre primero un coordinador.")
            return
        # Usar el primer coordinador o pedir selección
        dlg = _DialogoSelCoord(coords, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            ok, msg = self.ctrl.validar(id_, dlg.id_sel)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _rechazar_sel(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        dlg = DialogoRechazo(parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.rechazar(id_, dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _agregar_terna_sel(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        ok, msg = self.ctrl.agregar_a_terna(id_)
        (msg_ok if ok else msg_error)(self, msg)
        if ok: self.actualizar()

    def _aceptar_sel(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        ok, msg = self.ctrl.aceptar(id_)
        (msg_ok if ok else msg_error)(self, msg)
        if ok: self.actualizar()


class _DialogoSelCoord(QDialog):
    def __init__(self, coordinadores, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Coordinador")
        self.setMinimumWidth(360)
        self.id_sel = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 12)
        lay.addWidget(QLabel("<b>Seleccione el Coordinador validador:</b>"))
        self.lista = QListWidget()
        for c in coordinadores:
            item = QListWidgetItem(f"{c.nombre_completo}  [{c.cedula}]")
            item.setData(Qt.ItemDataRole.UserRole, c.id_coordinador)
            self.lista.addItem(item)
        self.lista.setCurrentRow(0)
        lay.addWidget(self.lista)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._ok)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)
        self.setStyleSheet(f"background:{SURFACE};")

    def _ok(self):
        item = self.lista.currentItem()
        if item:
            self.id_sel = item.data(Qt.ItemDataRole.UserRole)
            self.accept()


# ── Vista Terna ───────────────────────────────────────────────────────────────

class TernaVista(SeccionBase):
    def __init__(self, ctrl_terna, ctrl_post, ctrl_est, ctrl_oferta, parent=None):
        self.ctrl  = ctrl_terna
        self.ctrlP = ctrl_post
        self.ctrlE = ctrl_est
        self.ctrlO = ctrl_oferta
        super().__init__("👥  Ternas", parent)

    def _headers(self):
        return ["ID Terna", "Oferta", "# Postulaciones", "Completa", "Estado"]

    def _botones_extra(self):
        self.btn_detalle = QPushButton("📄  Ver Detalle")
        self.btn_enviar  = QPushButton("📤  Enviar a Empresa")
        self.btn_detalle.setEnabled(False)
        self.btn_enviar.setEnabled(False)
        return [(self.btn_detalle, BTN_SECONDARY), (self.btn_enviar, BTN_SUCCESS)]

    def _setup_base(self):
        super()._setup_base()
        self.btn_agregar.setVisible(False)
        self.btn_editar.setVisible(False)
        self.btn_detalle.clicked.connect(self._ver_detalle)
        self.btn_enviar.clicked.connect(self._enviar_sel)
        self._tabla.itemSelectionChanged.connect(self._sync_botones)

    def _sync_botones(self):
        id_ = self._tabla.id_sel()
        tiene = id_ is not None
        self.btn_detalle.setEnabled(tiene)
        self.btn_eliminar.setEnabled(tiene)
        if tiene:
            t = self.ctrl.obtener(id_)
            self.btn_enviar.setEnabled(
                t is not None and t.estado == EstadoTerna.ACTIVA and bool(t.id_postulaciones)
            )
        else:
            self.btn_enviar.setEnabled(False)

    def _cargar_filas(self):
        filas = []
        for t in self.ctrl.listar():
            oferta = self.ctrlO.obtener(t.id_oferta)
            completa = "✔" if t.esta_completa() else "✗"
            filas.append([
                t.id_terna,
                oferta.descripcion[:45] + "…" if oferta and len(oferta.descripcion) > 45
                else (oferta.descripcion if oferta else t.id_oferta),
                len(t.id_postulaciones),
                completa,
                t.estado,
            ])
        return filas

    def _on_agregar(self): pass
    def _on_editar(self, id_): pass

    def _on_eliminar(self, id_):
        if confirmar_eliminacion(self, "esta terna"):
            from modelo.repositorio import Repositorio
            repo = Repositorio()
            t = repo.obtener_terna(id_)
            if t:
                # Revertir estados de postulaciones
                for id_p in t.id_postulaciones:
                    p = repo.obtener_postulacion(id_p)
                    if p:
                        p.estado = EstadoPostulacion.VALIDADA
                        repo.actualizar_postulacion(p)
            self.ctrl.obtener(id_)
            from modelo.repositorio import Repositorio
            Repositorio().eliminar_terna(id_)
            Repositorio().guardar()
            msg_ok(self, "Terna eliminada.")
            self.actualizar()

    def _enviar_sel(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        ok, msg = self.ctrl.enviar_a_empresa(id_)
        (msg_ok if ok else msg_error)(self, msg)
        if ok: self.actualizar()

    def _ver_detalle(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        t = self.ctrl.obtener(id_)
        dlg = _DialogoDetalleTerna(t, self.ctrlP, self.ctrlE, self.ctrlO, parent=self)
        dlg.exec()
        self.actualizar()


class _DialogoDetalleTerna(QDialog):
    def __init__(self, terna, ctrl_post, ctrl_est, ctrl_oferta, parent=None):
        super().__init__(parent)
        self.terna = terna
        self.ctrl_post = ctrl_post
        self.ctrl_est  = ctrl_est
        self.ctrl_of   = ctrl_oferta
        self.setWindowTitle(f"Detalle – Terna {terna.id_terna}")
        self.setMinimumSize(600, 380)
        self.setStyleSheet(f"background:{SURFACE};{FORM_FIELD}")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        of = self.ctrl_of.obtener(terna.id_oferta)
        lay.addWidget(QLabel(
            f"<b>Oferta:</b> {of.descripcion if of else terna.id_oferta}<br>"
            f"<b>Estado terna:</b> {terna.estado}&nbsp;&nbsp;"
            f"<b>Lugares disponibles:</b> {terna.MAX - len(terna.id_postulaciones)}"
        ))

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{BORDER};"); sep.setMaximumHeight(1)
        lay.addWidget(sep)

        self.tabla = Tabla(["ID Post.", "Estudiante", "Ciclo", "Práctica Previa", "Estado Post."])
        lay.addWidget(self.tabla)

        bar = QHBoxLayout()
        self.btn_quitar = QPushButton("✕  Quitar de Terna")
        self.btn_quitar.setStyleSheet(BTN_DANGER)
        self.btn_quitar.setEnabled(False)
        bar.addStretch(); bar.addWidget(self.btn_quitar)
        lay.addLayout(bar)

        btn_cerrar = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btn_cerrar.rejected.connect(self.reject)
        lay.addWidget(btn_cerrar)

        self.btn_quitar.clicked.connect(self._quitar)
        self.tabla.itemSelectionChanged.connect(
            lambda: self.btn_quitar.setEnabled(self.tabla.id_sel() is not None)
        )
        self._cargar()

    def _cargar(self):
        filas = []
        for id_p in self.terna.id_postulaciones:
            p   = self.ctrl_post.obtener(id_p)
            est = self.ctrl_est.obtener(p.id_estudiante) if p else None
            filas.append([
                id_p,
                est.nombre_completo if est else "?",
                est.ciclo           if est else "?",
                "Sí" if (est and est.tiene_practica_previa) else "No",
                p.estado if p else "?",
            ])
        self.tabla.llenar(filas)

    def _quitar(self):
        id_p = self.tabla.id_sel()
        if not id_p: return
        from modelo.repositorio import Repositorio
        repo = Repositorio()
        self.terna.remover(id_p)
        repo.actualizar_terna(self.terna)
        p = repo.obtener_postulacion(id_p)
        if p:
            p.estado = EstadoPostulacion.VALIDADA
            repo.actualizar_postulacion(p)
        msg_ok(self, "Postulación removida de la terna.")
        self._cargar()
