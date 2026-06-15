"""
vista/reporte_vista.py
Sistema de reportes: exporta a PDF los datos del sistema (resumen del dashboard y
listados). Disponible solo para Coordinador y Administrador (controlado por el menú).
"""

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QFileDialog,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextDocument
from PyQt6.QtPrintSupport import QPrinter

from .widgets import (
    PRIMARY, BORDER, BG, SURFACE, TEXT_MUTED, BTN_PRIMARY, msg_ok, msg_error,
)


def _html_reporte(reporte: dict) -> str:
    """Construye el HTML del reporte que se renderiza a PDF."""
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    partes = [
        f'<h1 style="color:#1B4F8A; font-family:Arial; font-weight:normal;">{reporte["titulo"]}</h1>',
        f'<p style="color:#555; font-family:Arial; font-size:11px;">'
        f'SGPP – Universidad de Cuenca · Generado: {fecha}</p>',
        "<hr/>",
    ]

    stats = reporte.get("stats") or []
    if stats:
        celdas = "".join(
            f'<td style="padding:6px 16px; border:1px solid #ccc;">'
            f'<span style="font-size:16px; color:#1B4F8A;">{v}</span><br/>'
            f'<span style="font-size:10px; color:#555;">{t}</span></td>'
            for t, v in stats
        )
        partes.append(f'<table cellspacing="0"><tr>{celdas}</tr></table><br/>')

    for tab in reporte.get("tablas", []):
        partes.append(f'<h3 style="color:#1B4F8A; font-family:Arial; font-weight:normal;">{tab["titulo"]}</h3>')
        ths = "".join(
            f'<th style="background:#1B4F8A; color:white; padding:5px 8px; '
            f'font-weight:normal; text-align:left;">{h}</th>' for h in tab["headers"]
        )
        if tab["filas"]:
            trs = []
            for i, fila in enumerate(tab["filas"]):
                bg = "#EEF2FF" if i % 2 else "#FFFFFF"
                tds = "".join(
                    f'<td style="padding:4px 8px; border-bottom:1px solid #ddd;">'
                    f'{"" if c is None else c}</td>' for c in fila
                )
                trs.append(f'<tr style="background:{bg};">{tds}</tr>')
            cuerpo = "".join(trs)
        else:
            cuerpo = (f'<tr><td colspan="{len(tab["headers"])}" '
                      f'style="padding:8px; color:#888; font-style:italic;">'
                      f'Sin registros.</td></tr>')
        partes.append(
            f'<table width="100%" cellspacing="0" style="font-family:Arial; '
            f'font-size:11px; margin-bottom:14px;"><tr>{ths}</tr>{cuerpo}</table>'
        )

    return "<div>" + "".join(partes) + "</div>"


def exportar_pdf(parent, reporte: dict, nombre_sugerido: str):
    """Pide la ruta y escribe el reporte como PDF. Devuelve la ruta o None si se cancela."""
    ruta, _ = QFileDialog.getSaveFileName(
        parent, "Guardar reporte PDF", nombre_sugerido, "PDF (*.pdf)")
    if not ruta:
        return None
    if not ruta.lower().endswith(".pdf"):
        ruta += ".pdf"
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(ruta)
    doc = QTextDocument()
    doc.setHtml(_html_reporte(reporte))
    doc.print(printer)
    return ruta


class ReportesVista(QWidget):
    def __init__(self, ctrl_reporte, parent=None):
        super().__init__(parent)
        self.ctrl = ctrl_reporte
        self.setStyleSheet(f"background:{BG};")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        hdr = QLabel("📊  Reportes")
        hdr.setFont(QFont("Segoe UI", 17))
        hdr.setStyleSheet(f"color:{PRIMARY};")
        lay.addWidget(hdr)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{BORDER};"); sep.setMaximumHeight(1)
        lay.addWidget(sep)

        desc = QLabel("Genere y exporte reportes del sistema en formato PDF.")
        desc.setStyleSheet(f"color:{TEXT_MUTED};")
        lay.addWidget(desc)

        for clave, titulo in self.ctrl.disponibles():
            fila = QFrame()
            fila.setStyleSheet(
                f"QFrame {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:8px; }}"
            )
            fl = QHBoxLayout(fila)
            fl.setContentsMargins(16, 10, 16, 10)
            etq = QLabel(titulo)
            etq.setFont(QFont("Segoe UI", 12))
            etq.setStyleSheet("border:none;")
            btn = QPushButton("⬇  Exportar PDF")
            btn.setStyleSheet(BTN_PRIMARY)
            btn.setFixedHeight(32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _checked, c=clave: self._exportar(c))
            fl.addWidget(etq)
            fl.addStretch()
            fl.addWidget(btn)
            lay.addWidget(fila)

        lay.addStretch()

    def _exportar(self, clave):
        reporte = self.ctrl.generar(clave)
        try:
            ruta = exportar_pdf(self, reporte, f"reporte_{clave}.pdf")
        except Exception as e:
            msg_error(self, f"No se pudo generar el PDF:\n{e}")
            return
        if ruta:
            msg_ok(self, f"Reporte exportado correctamente:\n{ruta}")

    def actualizar(self):
        pass   # los datos se leen en el momento de exportar
