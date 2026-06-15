"""
vista/main_window.py
Ventana principal del Sistema de Gestión de Prácticas Pre-Profesionales.
Barra lateral de navegación + área de contenido (QStackedWidget).
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
    QStatusBar, QButtonGroup, QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from modelo.repositorio import Repositorio
from modelo.sesion import Sesion
from modelo import permisos
from controlador.controladores import (
    ControladorEmpresa, ControladorConvenio, ControladorOferta,
    ControladorTutor, ControladorCoordinador, ControladorEstudiante,
    ControladorPostulacion, ControladorTerna, ControladorPractica,
    ControladorSolicitud, ControladorUsuario, ControladorReporte,
)
from vista.dashboard_vista    import DashboardVista
from vista.empresa_vista      import EmpresaVista
from vista.estudiante_vista   import EstudianteVista
from vista.oferta_vista       import OfertaVista
from vista.postulacion_vista  import PostulacionVista, TernaVista
from vista.practica_vista     import PracticaVista
from vista.tutor_vista        import TutorVista, CoordinadorVista
from vista.solicitud_vista    import SolicitudVista
from vista.usuario_vista      import UsuarioVista
from vista.reporte_vista      import ReportesVista

# ── Paleta ────────────────────────────────────────────────────────────────────
SIDEBAR_BG    = "#0D2B55"
SIDEBAR_HOVER = "#1A3D70"
SIDEBAR_SEL   = "#1B4F8A"
SIDEBAR_MARK  = "#64B5F6"
TEXT_NAV      = "#B0BEC5"
TEXT_NAV_ACT  = "#FFFFFF"
HEADER_BG     = "#1B4F8A"
BG_CONTENT    = "#F4F6FA"


class _NavBtn(QPushButton):
    """Botón de navegación lateral estilizado."""
    STYLE = f"""
        QPushButton {{
            text-align: left;
            padding: 0 0 0 22px;
            color: {TEXT_NAV};
            font-size: 13px;
            font-weight:normal;
            border: none;
            background: transparent;
            border-left: 3px solid transparent;
        }}
        QPushButton:hover {{
            background: {SIDEBAR_HOVER};
            color: {TEXT_NAV_ACT};
        }}
        QPushButton:checked {{
            background: {SIDEBAR_SEL};
            color: {TEXT_NAV_ACT};
            border-left: 3px solid {SIDEBAR_MARK};
            font-weight:normal;
        }}
    """

    def __init__(self, texto: str, parent=None):
        super().__init__(texto, parent)
        self.setCheckable(True)
        self.setFixedHeight(46)
        self.setStyleSheet(self.STYLE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SGPP – Sistema de Gestión de Prácticas Pre-Profesionales")
        self.setMinimumSize(1100, 680)
        self.resize(1280, 760)
        self.relogin = False   # "Cerrar sesión" lo pone True para reabrir el login

        self._init_controllers()
        self._build_ui()

        # Seleccionar la primera sección VISIBLE para el rol (Estudiante no ve Dashboard).
        # Si el rol no tiene secciones (rol inválido), no se expone ninguna vista.
        visibles = permisos.secciones_visibles(Sesion().rol)
        if visibles and visibles[0] in self._nav_btns:
            primero = visibles[0]
            self._nav_btns[primero].setChecked(True)
            self._stack.setCurrentIndex(primero)
            vista = self._stack.currentWidget()
            if hasattr(vista, "actualizar"):
                vista.actualizar()
        else:
            self._stack.setCurrentWidget(self._pagina_vacia)  # rol sin secciones
        u = Sesion().usuario
        self._status(f"Sesión iniciada: {u.nombre} ({u.rol})" if u else "Sistema listo.")

    # ── controladores ─────────────────────────────────────────────────────────

    def _init_controllers(self):
        self.repo     = Repositorio()
        self.ctrl_emp = ControladorEmpresa()
        self.ctrl_conv= ControladorConvenio()
        self.ctrl_of  = ControladorOferta()
        self.ctrl_tut = ControladorTutor()
        self.ctrl_coord= ControladorCoordinador()
        self.ctrl_est = ControladorEstudiante()
        self.ctrl_post= ControladorPostulacion()
        self.ctrl_ter = ControladorTerna()
        self.ctrl_prac= ControladorPractica()
        self.ctrl_sol = ControladorSolicitud()
        self.ctrl_usuario = ControladorUsuario()
        self.ctrl_reporte = ControladorReporte()

    # ── UI principal ──────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Barra de título
        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_sidebar())
        body.addWidget(self._build_content(), stretch=1)
        root.addLayout(body, stretch=1)

        self._status_bar = QStatusBar()
        self._status_bar.setStyleSheet(
            f"background:{HEADER_BG}; color:white; font-size:12px; padding:2px 12px;"
        )
        self.setStatusBar(self._status_bar)

    def _build_header(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet(f"background:{HEADER_BG};")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(20, 0, 20, 0)

        ico = QLabel("🎓")
        ico.setFont(QFont("Segoe UI Emoji", 20))
        ico.setStyleSheet("color:white;")

        titulo = QLabel("Sistema de Gestión de Prácticas Pre-Profesionales")
        titulo.setFont(QFont("Segoe UI", 13))
        titulo.setStyleSheet("color:white;")

        subtitulo = QLabel("Universidad de Cuenca – Carrera de Computación")
        subtitulo.setFont(QFont("Segoe UI", 9))
        subtitulo.setStyleSheet("color:#90CAF9;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        u = Sesion().usuario
        info = QLabel(f"👤  {u.nombre} · {u.rol}" if u else "")
        info.setFont(QFont("Segoe UI", 9))
        info.setStyleSheet("color:white;")

        btn_logout = QPushButton("Cerrar sesión")
        btn_logout.setFixedHeight(30)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        # Botón blanco con texto azul: contrasta sobre el header azul.
        btn_logout.setStyleSheet(
            "QPushButton { background:#FFFFFF; color:#1B4F8A; border:none;"
            " padding:5px 14px; border-radius:4px; font-weight:normal; }"
            "QPushButton:hover { background:#E3F2FD; }"
        )
        btn_logout.clicked.connect(self._cerrar_sesion)

        lay.addWidget(ico)
        lay.addSpacing(10)
        lay.addWidget(titulo)
        lay.addStretch()
        lay.addWidget(subtitulo)
        lay.addSpacing(16)
        lay.addWidget(info)
        lay.addSpacing(10)
        lay.addWidget(btn_logout)
        return bar

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(f"background:{SIDEBAR_BG};")

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Logo / cabecera
        logo_area = QLabel("SGPP")
        logo_area.setFont(QFont("Segoe UI", 16))
        logo_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_area.setStyleSheet(
            f"color:white; background:{SIDEBAR_BG}; padding:18px 0 8px 0;"
        )
        lay.addWidget(logo_area)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background:#1E3A5F;"); sep.setMaximumHeight(1)
        lay.addWidget(sep)
        lay.addSpacing(6)

        nav_items = [
            ("🏠  Dashboard",         0),
            ("👩‍🎓  Estudiantes",       1),
            ("🏢  Empresas",           2),
            ("📋  Ofertas",            3),
            ("📝  Postulaciones",      4),
            ("👥  Ternas",             5),
            ("🎓  Prácticas",          6),
            ("👨‍🏫  Tutores",            7),
            ("👔  Coordinadores",      8),
            ("📩  Solicitudes",        9),
            ("👤  Usuarios",          10),
            ("📊  Reportes",          11),
        ]

        self._nav_btns  = {}          # idx -> _NavBtn (solo secciones visibles)
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        rol = Sesion().rol
        for texto, idx in nav_items:
            if not permisos.puede_ver(rol, idx):
                continue
            btn = _NavBtn(texto)
            self._btn_group.addButton(btn, idx)
            self._nav_btns[idx] = btn
            lay.addWidget(btn)
            btn.clicked.connect(lambda checked, i=idx: self._navegar(i))

        lay.addStretch()

        # Pie lateral
        pie = QLabel("UCuenca © 2026")
        pie.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pie.setStyleSheet(f"color:#455A64; font-size:10px; padding:8px 0;")
        lay.addWidget(pie)
        return sidebar

    def _build_content(self) -> QWidget:
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background:{BG_CONTENT};")

        self._dashboard  = DashboardVista(self.repo)
        self._vista_est  = EstudianteVista(self.ctrl_est)
        self._vista_emp  = EmpresaVista(self.ctrl_emp, self.ctrl_conv)
        self._vista_of   = OfertaVista(self.ctrl_of, self.ctrl_emp)
        self._vista_post = PostulacionVista(
            self.ctrl_post, self.ctrl_est, self.ctrl_of, self.ctrl_coord
        )
        self._vista_terna= TernaVista(
            self.ctrl_ter, self.ctrl_post, self.ctrl_est, self.ctrl_of
        )
        self._vista_prac = PracticaVista(
            self.ctrl_prac, self.ctrl_post, self.ctrl_est,
            self.ctrl_of, self.ctrl_emp,
            self.ctrl_tut, self.ctrl_tut,
        )
        self._vista_tut  = TutorVista(self.ctrl_tut)
        self._vista_coord= CoordinadorVista(self.ctrl_coord)
        self._vista_sol  = SolicitudVista(
            self.ctrl_sol, self.ctrl_est, self.ctrl_emp, self.ctrl_coord
        )
        self._vista_usuario = UsuarioVista(self.ctrl_usuario)
        self._vista_reporte = ReportesVista(self.ctrl_reporte)

        vistas = [
            self._dashboard, self._vista_est, self._vista_emp,
            self._vista_of,  self._vista_post,self._vista_terna,
            self._vista_prac,self._vista_tut, self._vista_coord,
            self._vista_sol, self._vista_usuario, self._vista_reporte,
        ]
        for v in vistas:
            self._stack.addWidget(v)

        # Página por defecto para roles sin secciones (rol inválido): no expone datos.
        self._pagina_vacia = QLabel("Sin secciones disponibles para este usuario.")
        self._pagina_vacia.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pagina_vacia.setStyleSheet("color:#757575; font-size:14px;")
        self._stack.addWidget(self._pagina_vacia)
        return self._stack

    # ── navegación ────────────────────────────────────────────────────────────

    _NOMBRES = [
        "Dashboard", "Estudiantes", "Empresas", "Ofertas de Práctica",
        "Postulaciones", "Ternas", "Prácticas", "Tutores",
        "Coordinadores", "Solicitudes", "Usuarios", "Reportes",
    ]

    def _navegar(self, idx: int):
        # Defensa en profundidad: nunca navegar a una sección no permitida para el rol
        if not permisos.puede_ver(Sesion().rol, idx):
            return
        self._stack.setCurrentIndex(idx)
        nombre = self._NOMBRES[idx] if idx < len(self._NOMBRES) else ""
        self._status(f"Sección: {nombre}")
        # Refrescar la vista activa
        vista = self._stack.currentWidget()
        if hasattr(vista, "actualizar"):
            vista.actualizar()
        if idx == 0:
            self._dashboard.actualizar()

    def _cerrar_sesion(self):
        """Marca relogin y cierra la ventana; el bucle de arranque reabre el login."""
        self.relogin = True
        self.close()

    def _status(self, msg: str):
        if hasattr(self, "_status_bar"):
            self._status_bar.showMessage(f"  {msg}")
