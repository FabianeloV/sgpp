"""
vista/widgets.py
Widgets reutilizables, estilos globales y clases base para la capa de vista.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel,
    QHeaderView, QMessageBox, QFrame, QSizePolicy,
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QCheckBox, QDateEdit, QSpinBox,
    QDialogButtonBox, QAbstractItemView,
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QBrush

# ── Paleta de colores ─────────────────────────────────────────────────────────
PRIMARY   = "#1B4F8A"
PRIMARY_L = "#2562AA"
PRIMARY_D = "#0D3166"
ACCENT    = "#1976D2"
DANGER    = "#C62828"
SUCCESS   = "#2E7D32"
WARNING   = "#E65100"
BG        = "#F4F6FA"
SURFACE   = "#FFFFFF"
BORDER    = "#E0E0E0"
TEXT      = "#212121"
TEXT_MUTED= "#757575"

# ── Estilos de botones ────────────────────────────────────────────────────────
BTN_PRIMARY = f"""
QPushButton {{
    background-color:{PRIMARY}; color:white; border:none;
    padding:6px 18px; border-radius:4px; font-weight:600;
}}
QPushButton:hover  {{ background-color:{PRIMARY_L}; }}
QPushButton:pressed{{ background-color:{PRIMARY_D}; }}
QPushButton:disabled{{ background-color:#BDBDBD; color:#9E9E9E; }}
"""
BTN_DANGER = f"""
QPushButton {{
    background-color:{DANGER}; color:white; border:none;
    padding:6px 18px; border-radius:4px; font-weight:600;
}}
QPushButton:hover  {{ background-color:#E53935; }}
QPushButton:disabled{{ background-color:#BDBDBD; color:#9E9E9E; }}
"""
BTN_SUCCESS = f"""
QPushButton {{
    background-color:{SUCCESS}; color:white; border:none;
    padding:6px 18px; border-radius:4px; font-weight:600;
}}
QPushButton:hover  {{ background-color:#43A047; }}
QPushButton:disabled{{ background-color:#BDBDBD; color:#9E9E9E; }}
"""
BTN_WARNING = f"""
QPushButton {{
    background-color:{WARNING}; color:white; border:none;
    padding:6px 18px; border-radius:4px; font-weight:600;
}}
QPushButton:hover  {{ background-color:#EF6C00; }}
QPushButton:disabled{{ background-color:#BDBDBD; color:#9E9E9E; }}
"""
BTN_SECONDARY = f"""
QPushButton {{
    background-color:#ECEFF1; color:{TEXT}; border:1px solid {BORDER};
    padding:6px 18px; border-radius:4px; font-weight:500;
}}
QPushButton:hover  {{ background-color:#CFD8DC; }}
"""

STYLE_TABLE = f"""
QTableWidget {{
    border:1px solid {BORDER}; gridline-color:{BORDER};
    background-color:{SURFACE}; alternate-background-color:#EEF2FF;
    selection-background-color:#BBDEFB; selection-color:{TEXT};
    font-size:13px;
}}
QTableWidget::item {{ padding:4px 8px; }}
QHeaderView::section {{
    background-color:{PRIMARY}; color:white;
    padding:7px 8px; border:none; font-weight:700; font-size:12px;
}}
QScrollBar:vertical {{
    border:none; background:{BG}; width:10px; margin:0;
}}
QScrollBar::handle:vertical {{
    background:#90A4AE; border-radius:5px; min-height:20px;
}}
"""

FORM_FIELD = f"""
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit {{
    border:1px solid {BORDER}; border-radius:4px; padding:5px 8px;
    background:{SURFACE}; font-size:13px;
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDateEdit:focus {{
    border:1px solid {ACCENT};
}}
"""

# ── helpers de diálogos ───────────────────────────────────────────────────────

def confirmar_eliminacion(parent: QWidget, nombre: str = "este registro") -> bool:
    r = QMessageBox.question(
        parent, "Confirmar Eliminación",
        f"¿Está seguro de eliminar {nombre}?\nEsta acción no se puede deshacer.",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return r == QMessageBox.StandardButton.Yes

def msg_error(parent, msg, titulo="Error"):
    QMessageBox.critical(parent, titulo, msg)

def msg_ok(parent, msg, titulo="Operación exitosa"):
    QMessageBox.information(parent, titulo, msg)

def msg_warn(parent, msg, titulo="Advertencia"):
    QMessageBox.warning(parent, titulo, msg)


# ── Tabla base reutilizable ───────────────────────────────────────────────────

class Tabla(QTableWidget):
    def __init__(self, headers: list, parent=None):
        super().__init__(parent)
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.setStyleSheet(STYLE_TABLE)
        self.setSortingEnabled(True)
        self.setShowGrid(True)

    def id_sel(self) -> str | None:
        """Devuelve el valor de la primera columna de la fila seleccionada."""
        row = self.currentRow()
        if row < 0: return None
        item = self.item(row, 0)
        return item.text() if item else None

    def llenar(self, filas: list[list]):
        self.setSortingEnabled(False)
        self.setRowCount(0)
        for fila in filas:
            r = self.rowCount()
            self.insertRow(r)
            for c, val in enumerate(fila):
                it = QTableWidgetItem(str(val) if val is not None else "")
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(r, c, it)
        self.setSortingEnabled(True)

    def colorear_fila(self, row: int, color: str):
        brush = QBrush(QColor(color))
        for c in range(self.columnCount()):
            item = self.item(row, c)
            if item:
                item.setBackground(brush)


# ── Sección CRUD base ─────────────────────────────────────────────────────────

class SeccionBase(QWidget):
    """
    Widget base para secciones CRUD.
    Subclases deben implementar: _headers(), _cargar_filas(),
    _on_agregar(), _on_editar(id_), _on_eliminar(id_).
    Pueden agregar botones extra con _botones_extra().
    """

    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        self.setObjectName("seccion")
        self.setStyleSheet(f"QWidget#seccion {{ background:{BG}; }}")
        self._titulo = titulo
        self._setup_base()
        self.actualizar()

    def _setup_base(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Cabecera
        hdr = QLabel(self._titulo)
        hdr.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
        hdr.setStyleSheet(f"color:{PRIMARY};")
        layout.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{BORDER};")
        sep.setMaximumHeight(1)
        layout.addWidget(sep)

        # Barra de botones
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(8)

        self.btn_agregar = QPushButton("＋  Agregar")
        self.btn_editar  = QPushButton("✏  Editar")
        self.btn_eliminar= QPushButton("✕  Eliminar")

        self.btn_agregar.setStyleSheet(BTN_PRIMARY)
        self.btn_editar.setStyleSheet(BTN_SECONDARY)
        self.btn_eliminar.setStyleSheet(BTN_DANGER)

        for b in [self.btn_agregar, self.btn_editar, self.btn_eliminar]:
            b.setFixedHeight(34)
            btn_bar.addWidget(b)

        # Botones extra del subclase
        for b, style in self._botones_extra():
            b.setStyleSheet(style)
            b.setFixedHeight(34)
            btn_bar.addWidget(b)

        btn_bar.addStretch()
        layout.addLayout(btn_bar)

        # Tabla
        self._tabla = Tabla(self._headers())
        layout.addWidget(self._tabla)

        # Conexiones base
        self.btn_agregar.clicked.connect(self._on_agregar)
        self.btn_editar.clicked.connect(self._editar_sel)
        self.btn_eliminar.clicked.connect(self._eliminar_sel)
        self._tabla.itemSelectionChanged.connect(self._actualizar_botones)
        self._actualizar_botones()

    def _headers(self) -> list:
        return ["ID"]

    def _botones_extra(self) -> list:
        """Retorna lista de (QPushButton, style_str) para botones adicionales."""
        return []

    def _cargar_filas(self) -> list:
        return []

    def _on_agregar(self): pass
    def _on_editar(self, id_: str): pass
    def _on_eliminar(self, id_: str): pass

    def _editar_sel(self):
        id_ = self._tabla.id_sel()
        if id_: self._on_editar(id_)

    def _eliminar_sel(self):
        id_ = self._tabla.id_sel()
        if id_: self._on_eliminar(id_)

    def _actualizar_botones(self):
        tiene = self._tabla.id_sel() is not None
        self.btn_editar.setEnabled(tiene)
        self.btn_eliminar.setEnabled(tiene)

    def actualizar(self):
        self._tabla.llenar(self._cargar_filas())
        self._actualizar_botones()


# ── Diálogos base ─────────────────────────────────────────────────────────────

class DialogoBase(QDialog):
    """Diálogo de formulario estándar."""

    def __init__(self, titulo: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setMinimumWidth(460)
        self.setModal(True)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 20, 20, 16)
        self._layout.setSpacing(12)

        hdr = QLabel(titulo)
        hdr.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        hdr.setStyleSheet(f"color:{PRIMARY};")
        self._layout.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{BORDER};")
        sep.setMaximumHeight(1)
        self._layout.addWidget(sep)

        self._form = QFormLayout()
        self._form.setSpacing(10)
        self._form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self._layout.addLayout(self._form)

        self._layout.addSpacing(6)
        self._build_buttons()
        self.setStyleSheet(FORM_FIELD + f"QDialog{{background:{SURFACE};}}")

    def _build_buttons(self):
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Guardar")
        btns.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(BTN_PRIMARY)
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet(BTN_SECONDARY)
        btns.accepted.connect(self._aceptar)
        btns.rejected.connect(self.reject)
        self._layout.addWidget(btns)

    def _aceptar(self):
        self.accept()

    def _agregar_campo(self, label: str, widget: QWidget, required=False):
        lbl_text = f"<b>{label}</b>:" if required else f"{label}:"
        self._form.addRow(QLabel(lbl_text), widget)

    def _campo_texto(self, placeholder="") -> QLineEdit:
        w = QLineEdit()
        w.setPlaceholderText(placeholder)
        return w

    def _campo_combo(self, opciones: list) -> QComboBox:
        w = QComboBox()
        for op in opciones:
            if isinstance(op, tuple):
                w.addItem(op[0], op[1])
            else:
                w.addItem(str(op), op)
        return w

    def _campo_fecha(self, valor: str | None = None) -> QDateEdit:
        w = QDateEdit()
        w.setCalendarPopup(True)
        w.setDisplayFormat("yyyy-MM-dd")
        if valor:
            parts = valor.split("-")
            w.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
        else:
            w.setDate(QDate.currentDate())
        return w

    def _campo_spin(self, min_=1, max_=10, val=1) -> QSpinBox:
        w = QSpinBox()
        w.setRange(min_, max_)
        w.setValue(val)
        return w

    def _campo_check(self, texto="") -> QCheckBox:
        return QCheckBox(texto)

    def _campo_area(self, placeholder="", alto=70) -> QTextEdit:
        w = QTextEdit()
        w.setPlaceholderText(placeholder)
        w.setFixedHeight(alto)
        return w
