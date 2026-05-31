"""
vista/dashboard_vista.py
Panel de resumen con estadísticas y estado del sistema.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QAbstractItemView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from .widgets import PRIMARY, BORDER, SURFACE, BG, TEXT, TEXT_MUTED


class _TarjetaStat(QFrame):
    def __init__(self, titulo: str, valor: str, color: str, icono: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background:{SURFACE};
                border-radius:10px;
                border:1px solid {BORDER};
            }}
        """)
        self.setFixedHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 12, 18, 12)
        lay.setSpacing(14)

        # Icono
        ico = QLabel(icono)
        ico.setFont(QFont("Segoe UI Emoji", 28))
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setFixedWidth(50)
        lay.addWidget(ico)

        # Textos
        txt_lay = QVBoxLayout()
        txt_lay.setSpacing(2)
        lbl_val = QLabel(valor)
        lbl_val.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        lbl_val.setStyleSheet(f"color:{color}; border:none;")
        lbl_tit = QLabel(titulo)
        lbl_tit.setFont(QFont("Segoe UI", 11))
        lbl_tit.setStyleSheet(f"color:{TEXT_MUTED}; border:none;")
        txt_lay.addWidget(lbl_val)
        txt_lay.addWidget(lbl_tit)
        lay.addLayout(txt_lay)
        lay.addStretch()


class _MiniTabla(QTableWidget):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet(f"""
            QTableWidget {{
                border:1px solid {BORDER};
                alternate-background-color:#EEF2FF;
                background:{SURFACE};
                font-size:12px;
            }}
            QHeaderView::section {{
                background:#37474F; color:white;
                padding:5px 6px; border:none; font-weight:700;
            }}
        """)
        self.setMaximumHeight(200)

    def llenar(self, filas):
        self.setRowCount(0)
        for fila in filas:
            r = self.rowCount()
            self.insertRow(r)
            for c, val in enumerate(fila):
                it = QTableWidgetItem(str(val) if val is not None else "")
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(r, c, it)


class DashboardVista(QWidget):
    def __init__(self, repositorio, parent=None):
        super().__init__(parent)
        self.repo = repositorio
        self.setStyleSheet(f"background:{BG};")
        self._build_ui()

    def _build_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content.setStyleSheet(f"background:{BG};")
        main = QVBoxLayout(content)
        main.setContentsMargins(24, 20, 24, 24)
        main.setSpacing(20)

        # Título
        hdr = QLabel("Panel de Control – SGPP")
        hdr.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        hdr.setStyleSheet(f"color:{PRIMARY};")
        main.addWidget(hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{BORDER};"); sep.setMaximumHeight(1)
        main.addWidget(sep)

        # Tarjetas
        self._grid_stats = QGridLayout()
        self._grid_stats.setSpacing(14)
        main.addLayout(self._grid_stats)

        # Tablas de resumen
        self._sec_practicas = self._seccion("🎓  Prácticas Activas",
            ["ID Práctica", "Estudiante", "Empresa", "Desde"])
        self._sec_pend = self._seccion("📝  Postulaciones Pendientes",
            ["ID", "Estudiante", "Oferta", "Fecha"])
        self._sec_ternas = self._seccion("👥  Ternas Pendientes de Enviar",
            ["ID Terna", "Oferta", "# Posts"])
        self._sec_sol = self._seccion("📩  Solicitudes Pendientes",
            ["ID", "Estudiante", "Tipo", "Fecha"])

        col_lay = QHBoxLayout()
        col_lay.setSpacing(16)
        izq = QVBoxLayout(); izq.setSpacing(16)
        der = QVBoxLayout(); der.setSpacing(16)
        izq.addWidget(self._sec_practicas)
        izq.addWidget(self._sec_ternas)
        der.addWidget(self._sec_pend)
        der.addWidget(self._sec_sol)
        col_lay.addLayout(izq)
        col_lay.addLayout(der)
        main.addLayout(col_lay)
        main.addStretch()

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _seccion(self, titulo, headers):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{ background:{SURFACE}; border-radius:8px;
                      border:1px solid {BORDER}; }}
        """)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)
        lbl = QLabel(titulo)
        lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color:{PRIMARY}; border:none;")
        lay.addWidget(lbl)
        tabla = _MiniTabla(headers)
        lay.addWidget(tabla)
        frame._tabla = tabla
        return frame

    def actualizar(self):
        repo = self.repo
        practicas  = repo.listar_practicas()
        estudiantes= repo.listar_estudiantes()
        empresas   = repo.listar_empresas()
        ofertas    = repo.listar_ofertas()
        posts      = repo.listar_postulaciones()
        ternas     = repo.listar_ternas()
        solicitudes= repo.listar_solicitudes()

        from modelo.entidades import EstadoPractica, EstadoPostulacion, EstadoTerna, EstadoSolicitud
        act_prac = [p for p in practicas  if p.estado == EstadoPractica.ACTIVA]
        pend_post= [p for p in posts       if p.estado == EstadoPostulacion.PENDIENTE]
        pend_ter = [t for t in ternas      if t.estado == EstadoTerna.ACTIVA]
        pend_sol = [s for s in solicitudes if s.estado == EstadoSolicitud.PENDIENTE]

        # Limpiar y refrescar tarjetas
        while self._grid_stats.count():
            item = self._grid_stats.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        stats = [
            ("Estudiantes",      str(len(estudiantes)), "#1B4F8A", "👩‍🎓"),
            ("Empresas",         str(len(empresas)),    "#1565C0", "🏢"),
            ("Ofertas Activas",  str(sum(1 for o in ofertas if o.estado=="Activa")), "#2E7D32", "📋"),
            ("Postul. Pendientes",str(len(pend_post)),  "#E65100", "📝"),
            ("Prácticas Activas",str(len(act_prac)),    "#6A1B9A", "🎓"),
            ("Solicitudes Pend.", str(len(pend_sol)),   "#C62828", "📩"),
        ]
        for i, (titulo, valor, color, icono) in enumerate(stats):
            card = _TarjetaStat(titulo, valor, color, icono)
            self._grid_stats.addWidget(card, i // 3, i % 3)

        # Prácticas activas
        filas_prac = []
        for p in act_prac:
            post = repo.obtener_postulacion(p.id_postulacion)
            est  = repo.obtener_estudiante(post.id_estudiante) if post else None
            of   = repo.obtener_oferta(post.id_oferta)         if post else None
            emp  = repo.obtener_empresa(of.id_empresa)          if of   else None
            filas_prac.append([
                p.id_practica,
                est.nombre_completo if est else "?",
                emp.nombre          if emp else "?",
                p.fecha_inicio,
            ])
        self._sec_practicas._tabla.llenar(filas_prac)

        # Postulaciones pendientes
        filas_pp = []
        for p in pend_post[:15]:
            est = repo.obtener_estudiante(p.id_estudiante)
            of  = repo.obtener_oferta(p.id_oferta)
            filas_pp.append([
                p.id_postulacion,
                est.nombre_completo if est else "?",
                of.descripcion[:40] if of else "?",
                p.fecha,
            ])
        self._sec_pend._tabla.llenar(filas_pp)

        # Ternas
        filas_ter = []
        for t in pend_ter:
            of = repo.obtener_oferta(t.id_oferta)
            filas_ter.append([
                t.id_terna,
                of.descripcion[:40] if of else "?",
                len(t.id_postulaciones),
            ])
        self._sec_ternas._tabla.llenar(filas_ter)

        # Solicitudes
        filas_sol = []
        for s in pend_sol[:15]:
            est = repo.obtener_estudiante(s.id_estudiante)
            filas_sol.append([s.id_solicitud, est.nombre_completo if est else "?",
                               s.tipo, s.fecha])
        self._sec_sol._tabla.llenar(filas_sol)
