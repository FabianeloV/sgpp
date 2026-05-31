"""
vista/practica_vista.py
Vista principal de Prácticas: creación, seguimiento, actividades y formularios.
"""

from PyQt6.QtWidgets import (
    QPushButton, QLabel, QDialog, QVBoxLayout, QHBoxLayout,
    QTabWidget, QWidget, QFrame, QDialogButtonBox, QTextEdit,
    QListWidget, QListWidgetItem,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from modelo.entidades import EstadoPostulacion, EstadoPractica, TipoFormulario
from .widgets import (
    SeccionBase, DialogoBase, Tabla,
    BTN_PRIMARY, BTN_SECONDARY, BTN_SUCCESS, BTN_WARNING, BTN_DANGER,
    PRIMARY, BORDER, SURFACE, BG, FORM_FIELD,
    confirmar_eliminacion, msg_error, msg_ok, msg_warn,
)


# ── Diálogo crear práctica ────────────────────────────────────────────────────

class DialogoCrearPractica(DialogoBase):
    def __init__(self, postulaciones_acept, tutores_ac, tutores_emp, parent=None):
        super().__init__("Crear Nueva Práctica", parent)
        self.setMinimumWidth(500)

        self.cmb_post = self._campo_combo([
            (f"{p._label}", p.id_postulacion) for p in postulaciones_acept
        ])
        self.cmb_tac  = self._campo_combo(
            [(f"{t.nombre_completo} – {t.area}", t.id_tutor) for t in tutores_ac]
        )
        self.cmb_temp = self._campo_combo(
            [(f"{t.nombre_completo} – {t.cargo}", t.id_tutor) for t in tutores_emp]
        )
        self.fecha_ini = self._campo_fecha()

        self._agregar_campo("Postulación Aceptada *",  self.cmb_post,  True)
        self._agregar_campo("Tutor Académico *",        self.cmb_tac,   True)
        self._agregar_campo("Tutor Empresarial *",      self.cmb_temp,  True)
        self._agregar_campo("Fecha de Inicio *",        self.fecha_ini, True)

    def datos(self):
        return (
            self.cmb_post.currentData(),
            self.cmb_tac.currentData(),
            self.cmb_temp.currentData(),
            self.fecha_ini.date().toString("yyyy-MM-dd"),
        )


# ── Vista principal de Prácticas ──────────────────────────────────────────────

class PracticaVista(SeccionBase):
    def __init__(self, ctrl_prac, ctrl_post, ctrl_est,
                 ctrl_oferta, ctrl_emp, ctrl_tac, ctrl_temp, parent=None):
        self.ctrl  = ctrl_prac
        self.ctrlP = ctrl_post
        self.ctrlE = ctrl_est
        self.ctrlO = ctrl_oferta
        self.ctrlEmp = ctrl_emp
        self.ctrlTA  = ctrl_tac
        self.ctrlTE  = ctrl_temp
        super().__init__("🎓  Prácticas Pre-Profesionales", parent)

    def _headers(self):
        return ["ID", "Estudiante", "Empresa", "Fecha Inicio", "Estado", "T. Académico", "T. Empresarial"]

    def _botones_extra(self):
        self.btn_nuevo    = QPushButton("＋  Nueva Práctica")
        self.btn_detalle  = QPushButton("🔍  Detalle")
        self.btn_finalizar= QPushButton("🏁  Finalizar")
        self.btn_aprobar  = QPushButton("✅  Aprobar")
        for b in [self.btn_detalle, self.btn_finalizar, self.btn_aprobar]:
            b.setEnabled(False)
        return [
            (self.btn_nuevo,    BTN_PRIMARY),
            (self.btn_detalle,  BTN_SECONDARY),
            (self.btn_finalizar,BTN_WARNING),
            (self.btn_aprobar,  BTN_SUCCESS),
        ]

    def _setup_base(self):
        super()._setup_base()
        self.btn_agregar.setVisible(False)
        self.btn_nuevo.clicked.connect(self._crear_practica)
        self.btn_detalle.clicked.connect(self._ver_detalle)
        self.btn_finalizar.clicked.connect(self._finalizar_sel)
        self.btn_aprobar.clicked.connect(self._aprobar_sel)
        self._tabla.itemSelectionChanged.connect(self._sync_botones)

    def _sync_botones(self):
        id_ = self._tabla.id_sel()
        if not id_:
            for b in [self.btn_detalle, self.btn_finalizar,
                      self.btn_aprobar, self.btn_editar, self.btn_eliminar]:
                b.setEnabled(False)
            return
        p = self.ctrl.obtener(id_)
        if not p: return
        self.btn_detalle.setEnabled(True)
        self.btn_finalizar.setEnabled(p.estado == EstadoPractica.ACTIVA)
        self.btn_aprobar.setEnabled(p.estado == EstadoPractica.FINALIZADA)
        self.btn_editar.setEnabled(False)
        self.btn_eliminar.setEnabled(True)

    def _cargar_filas(self):
        filas = []
        for p in self.ctrl.listar():
            post = self.ctrlP.obtener(p.id_postulacion)
            est  = self.ctrlE.obtener(post.id_estudiante) if post else None
            of   = self.ctrlO.obtener(post.id_oferta) if post else None
            emp  = self.ctrlEmp.obtener(of.id_empresa) if of else None
            ta   = self.ctrlTA.obtener_academico(p.id_t_academico)
            te   = self.ctrlTE.obtener_empresarial(p.id_t_empresarial)
            filas.append([
                p.id_practica,
                est.nombre_completo if est else "?",
                emp.nombre          if emp else "?",
                p.fecha_inicio,
                p.estado,
                ta.nombre_completo  if ta  else "?",
                te.nombre_completo  if te  else "?",
            ])
        return filas

    def actualizar(self):
        super().actualizar()
        colores = {
            EstadoPractica.ACTIVA:     "#E8F5E9",
            EstadoPractica.FINALIZADA: "#FFF8E1",
            EstadoPractica.APROBADA:   "#E3F2FD",
            EstadoPractica.SUSPENDIDA: "#FFEBEE",
        }
        from PyQt6.QtGui import QBrush, QColor
        for row in range(self._tabla.rowCount()):
            item = self._tabla.item(row, 4)
            if item:
                color = colores.get(item.text(), "#FFFFFF")
                b = QBrush(QColor(color))
                for c in range(self._tabla.columnCount()):
                    i = self._tabla.item(row, c)
                    if i: i.setBackground(b)

    def _on_agregar(self): self._crear_practica()
    def _on_editar(self, id_): pass

    def _on_eliminar(self, id_):
        if confirmar_eliminacion(self, "esta práctica"):
            ok, msg = self.ctrl.eliminar(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _crear_practica(self):
        # Recopilar postulaciones aceptadas sin práctica
        from modelo.repositorio import Repositorio
        repo = Repositorio()
        posts_acept = []
        for p in self.ctrlP.listar():
            if p.estado == EstadoPostulacion.ACEPTADA:
                if not repo.practica_de_postulacion(p.id_postulacion):
                    est = self.ctrlE.obtener(p.id_estudiante)
                    of  = self.ctrlO.obtener(p.id_oferta)
                    label = (f"{est.nombre_completo if est else '?'} → "
                             f"{of.descripcion[:30] if of else '?'}")
                    p._label = label
                    posts_acept.append(p)

        if not posts_acept:
            msg_warn(self, "No hay postulaciones aceptadas disponibles para crear una práctica.\n"
                           "Primero acepte una postulación en la sección Postulaciones.")
            return
        tac = self.ctrlTA.listar_academicos()
        tep = self.ctrlTE.listar_empresariales()
        if not tac:
            msg_warn(self, "Registre al menos un Tutor Académico.")
            return
        if not tep:
            msg_warn(self, "Registre al menos un Tutor Empresarial.")
            return

        dlg = DialogoCrearPractica(posts_acept, tac, tep, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            ok, msg = self.ctrl.crear(*dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _finalizar_sel(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        dlg = _DialogoFinalizar(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            ok, msg = self.ctrl.finalizar(id_, *dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _aprobar_sel(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        ok, msg = self.ctrl.aprobar(id_)
        (msg_ok if ok else msg_error)(self, msg)
        if ok: self.actualizar()

    def _ver_detalle(self):
        id_ = self._tabla.id_sel()
        if not id_: return
        p = self.ctrl.obtener(id_)
        dlg = _DialogoDetallePractica(
            p, self.ctrl, self.ctrlP, self.ctrlE,
            self.ctrlO, self.ctrlEmp, self.ctrlTA, self.ctrlTE,
            parent=self
        )
        dlg.exec()
        self.actualizar()


class _DialogoFinalizar(DialogoBase):
    def __init__(self, parent=None):
        super().__init__("Finalizar Práctica", parent)
        self.fecha_fin = self._campo_fecha()
        self.txt_obs   = self._campo_area("Observaciones finales…")
        self._agregar_campo("Fecha de Fin *",  self.fecha_fin, True)
        self._agregar_campo("Observaciones",   self.txt_obs)

    def datos(self):
        return self.fecha_fin.date().toString("yyyy-MM-dd"), self.txt_obs.toPlainText()


# ── Detalle completo de la práctica ──────────────────────────────────────────

class _DialogoDetallePractica(QDialog):
    def __init__(self, practica, ctrl, ctrl_post, ctrl_est,
                 ctrl_of, ctrl_emp, ctrl_ta, ctrl_te, parent=None):
        super().__init__(parent)
        self.prac  = practica
        self.ctrl  = ctrl
        self.ctrlP = ctrl_post
        self.ctrlE = ctrl_est
        self.ctrlO = ctrl_of
        self.ctrlEmp = ctrl_emp
        self.ctrlTA = ctrl_ta
        self.ctrlTE = ctrl_te

        self.setWindowTitle(f"Detalle Práctica – {practica.id_practica}")
        self.setMinimumSize(780, 560)
        self.setStyleSheet(f"background:{BG};{FORM_FIELD}")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 12)
        lay.setSpacing(10)

        # Info cabecera
        post = self.ctrlP.obtener(practica.id_postulacion)
        est  = self.ctrlE.obtener(post.id_estudiante) if post else None
        of   = self.ctrlO.obtener(post.id_oferta)     if post else None
        emp  = self.ctrlEmp.obtener(of.id_empresa)    if of   else None
        ta   = self.ctrlTA.obtener_academico(practica.id_t_academico)
        te   = self.ctrlTE.obtener_empresarial(practica.id_t_empresarial)

        info = (
            f"<b>Estudiante:</b> {est.nombre_completo if est else '?'} &nbsp;|&nbsp; "
            f"<b>Empresa:</b> {emp.nombre if emp else '?'} &nbsp;|&nbsp; "
            f"<b>Estado:</b> {practica.estado}<br>"
            f"<b>Inicio:</b> {practica.fecha_inicio} &nbsp; "
            f"<b>Fin:</b> {practica.fecha_fin or '—'} &nbsp;|&nbsp; "
            f"<b>T. Acad.:</b> {ta.nombre_completo if ta else '?'} &nbsp; "
            f"<b>T. Emp.:</b> {te.nombre_completo if te else '?'}"
        )
        lbl = QLabel(info)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"background:{SURFACE}; padding:10px; border-radius:6px; "
                          f"border:1px solid {BORDER};")
        lay.addWidget(lbl)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(f"QTabWidget::pane{{background:{SURFACE};}}")
        tabs.addTab(self._tab_actividades(), "📌  Actividades")
        tabs.addTab(self._tab_formularios(), "📄  Formularios")
        lay.addWidget(tabs)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    # ── Tab Actividades ───────────────────────────────────────────────────────

    def _tab_actividades(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        bar = QHBoxLayout()
        self.btn_act_add = QPushButton("＋ Agregar")
        self.btn_act_val = QPushButton("✔ Validar")
        self.btn_act_del = QPushButton("✕ Eliminar")
        self.btn_act_add.setStyleSheet(BTN_PRIMARY)
        self.btn_act_val.setStyleSheet(BTN_SUCCESS)
        self.btn_act_del.setStyleSheet(BTN_DANGER)
        for b in [self.btn_act_val, self.btn_act_del]:
            b.setEnabled(False)
        bar.addWidget(self.btn_act_add)
        bar.addWidget(self.btn_act_val)
        bar.addWidget(self.btn_act_del)
        bar.addStretch()
        lay.addLayout(bar)

        self.tab_act = Tabla(["ID", "Descripción", "Fecha", "Validada", "Tutor Valida"])
        lay.addWidget(self.tab_act)

        self.btn_act_add.clicked.connect(self._agregar_actividad)
        self.btn_act_val.clicked.connect(self._validar_actividad)
        self.btn_act_del.clicked.connect(self._eliminar_actividad)
        self.tab_act.itemSelectionChanged.connect(
            lambda: (self.btn_act_val.setEnabled(self.tab_act.id_sel() is not None),
                     self.btn_act_del.setEnabled(self.tab_act.id_sel() is not None))
        )
        self._cargar_actividades()
        return w

    def _cargar_actividades(self):
        from modelo.repositorio import Repositorio
        acts = Repositorio().actividades_practica(self.prac.id_practica)
        filas = []
        for a in acts:
            ta = self.ctrlTA.obtener_academico(a.id_tutor_valida) if a.id_tutor_valida else None
            filas.append([
                a.id_actividad,
                a.descripcion[:55] + "…" if len(a.descripcion) > 55 else a.descripcion,
                a.fecha,
                "✔" if a.validada else "✗",
                ta.nombre_completo if ta else "—",
            ])
        self.tab_act.llenar(filas)

    def _agregar_actividad(self):
        dlg = _DlgActividad(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            desc, fecha = dlg.datos()
            ok, msg = self.ctrl.agregar_actividad(self.prac.id_practica, desc, fecha)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self._cargar_actividades()

    def _validar_actividad(self):
        id_ = self.tab_act.id_sel()
        if not id_: return
        tutores = self.ctrlTA.listar_academicos()
        if not tutores:
            msg_warn(self, "No hay tutores académicos registrados.")
            return
        dlg = _DlgSelTutor(tutores, "Tutor Académico", parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            ok, msg = self.ctrl.validar_actividad(id_, dlg.id_sel)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self._cargar_actividades()

    def _eliminar_actividad(self):
        id_ = self.tab_act.id_sel()
        if id_ and confirmar_eliminacion(self, "esta actividad"):
            ok, msg = self.ctrl.eliminar_actividad(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self._cargar_actividades()

    # ── Tab Formularios ───────────────────────────────────────────────────────

    def _tab_formularios(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        bar = QHBoxLayout()
        self.btn_form_add  = QPushButton("＋ Agregar Formulario")
        self.btn_form_edit = QPushButton("✏ Editar")
        self.btn_form_del  = QPushButton("✕ Eliminar")
        self.btn_form_add.setStyleSheet(BTN_PRIMARY)
        self.btn_form_edit.setStyleSheet(BTN_SECONDARY)
        self.btn_form_del.setStyleSheet(BTN_DANGER)
        for b in [self.btn_form_edit, self.btn_form_del]: b.setEnabled(False)
        bar.addWidget(self.btn_form_add)
        bar.addWidget(self.btn_form_edit)
        bar.addWidget(self.btn_form_del)
        bar.addStretch()
        lay.addLayout(bar)

        nota = QLabel(
            "ℹ  El Formulario 1 se genera automáticamente al crear la práctica.  "
            "Los Formularios 2 y 3 deben agregarse al finalizar."
        )
        nota.setWordWrap(True)
        nota.setStyleSheet(f"color:#555; font-size:11px; padding:4px;")
        lay.addWidget(nota)

        self.tab_form = Tabla(["ID", "Tipo", "Fecha", "Firmado", "Observaciones"])
        lay.addWidget(self.tab_form)

        self.btn_form_add.clicked.connect(self._agregar_formulario)
        self.btn_form_edit.clicked.connect(self._editar_formulario)
        self.btn_form_del.clicked.connect(self._eliminar_formulario)
        self.tab_form.itemSelectionChanged.connect(
            lambda: (self.btn_form_edit.setEnabled(self.tab_form.id_sel() is not None),
                     self.btn_form_del.setEnabled(self.tab_form.id_sel() is not None))
        )
        self._cargar_formularios()
        return w

    def _cargar_formularios(self):
        from modelo.repositorio import Repositorio
        forms = Repositorio().formularios_practica(self.prac.id_practica)
        self.tab_form.llenar([
            [f.id_formulario, f.nombre, f.fecha,
             "✔" if f.firmado else "✗", f.observaciones[:40]]
            for f in forms
        ])

    def _agregar_formulario(self):
        from modelo.repositorio import Repositorio
        ya = {f.tipo for f in Repositorio().formularios_practica(self.prac.id_practica)}
        disponibles = [t for t in TipoFormulario.TODOS if t not in ya]
        if not disponibles:
            msg_warn(self, "Ya se registraron los tres formularios para esta práctica.")
            return
        dlg = _DlgFormulario(disponibles, practica_estado=self.prac.estado, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            tipo, fecha, firmado, obs = dlg.datos()
            ok, msg = self.ctrl.agregar_formulario(
                self.prac.id_practica, tipo, fecha, firmado, obs
            )
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self._cargar_formularios()

    def _editar_formulario(self):
        id_ = self.tab_form.id_sel()
        if not id_: return
        from modelo.repositorio import Repositorio
        f = Repositorio().obtener_formulario(id_)
        dlg = _DlgFormularioEdit(f, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            firmado, obs = dlg.datos()
            ok, msg = self.ctrl.actualizar_formulario(id_, firmado, obs)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self._cargar_formularios()

    def _eliminar_formulario(self):
        id_ = self.tab_form.id_sel()
        if id_ and confirmar_eliminacion(self, "este formulario"):
            ok, msg = self.ctrl.eliminar_formulario(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self._cargar_formularios()


# ── Diálogos auxiliares ───────────────────────────────────────────────────────

class _DlgActividad(DialogoBase):
    def __init__(self, parent=None):
        super().__init__("Nueva Actividad", parent)
        self.txt_desc = self._campo_area("Descripción de la actividad…", 80)
        self.fecha    = self._campo_fecha()
        self._agregar_campo("Descripción *", self.txt_desc, True)
        self._agregar_campo("Fecha *",       self.fecha,    True)

    def datos(self):
        return self.txt_desc.toPlainText(), self.fecha.date().toString("yyyy-MM-dd")


class _DlgSelTutor(QDialog):
    def __init__(self, tutores, titulo="Tutor", parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Seleccionar {titulo}")
        self.setMinimumWidth(340)
        self.id_sel = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 12)
        lay.addWidget(QLabel(f"<b>Seleccione el {titulo}:</b>"))
        self.lista = QListWidget()
        for t in tutores:
            item = QListWidgetItem(t.nombre_completo)
            item.setData(Qt.ItemDataRole.UserRole, t.id_tutor)
            self.lista.addItem(item)
        self.lista.setCurrentRow(0)
        lay.addWidget(self.lista)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._ok); btns.rejected.connect(self.reject)
        lay.addWidget(btns)
        self.setStyleSheet(f"background:{SURFACE};")

    def _ok(self):
        item = self.lista.currentItem()
        if item:
            self.id_sel = item.data(Qt.ItemDataRole.UserRole)
            self.accept()


class _DlgFormulario(DialogoBase):
    def __init__(self, tipos_disponibles, practica_estado="", parent=None):
        super().__init__("Agregar Formulario", parent)
        self.cmb_tipo = self._campo_combo(
            [(TipoFormulario.NOMBRES[t], t) for t in tipos_disponibles]
        )
        self.fecha   = self._campo_fecha()
        self.chk_firmado = self._campo_check("Firmado")
        self.txt_obs = self._campo_area("Observaciones…", 60)
        self._agregar_campo("Tipo *",        self.cmb_tipo, True)
        self._agregar_campo("Fecha *",       self.fecha,    True)
        self._agregar_campo("Estado",        self.chk_firmado)
        self._agregar_campo("Observaciones", self.txt_obs)

    def datos(self):
        return (
            self.cmb_tipo.currentData(),
            self.fecha.date().toString("yyyy-MM-dd"),
            self.chk_firmado.isChecked(),
            self.txt_obs.toPlainText(),
        )


class _DlgFormularioEdit(DialogoBase):
    def __init__(self, formulario, parent=None):
        super().__init__(f"Editar – {formulario.nombre}", parent)
        self.chk_firmado = self._campo_check("Firmado")
        self.chk_firmado.setChecked(formulario.firmado)
        self.txt_obs = self._campo_area("Observaciones…", 60)
        self.txt_obs.setPlainText(formulario.observaciones)
        self._agregar_campo("Estado",        self.chk_firmado)
        self._agregar_campo("Observaciones", self.txt_obs)

    def datos(self):
        return self.chk_firmado.isChecked(), self.txt_obs.toPlainText()
