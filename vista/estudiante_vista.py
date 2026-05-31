"""
vista/estudiante_vista.py
Vista de gestión de Estudiantes.
"""

from PyQt6.QtWidgets import QPushButton
from .widgets import (
    SeccionBase, DialogoBase, BTN_SECONDARY,
    confirmar_eliminacion, msg_error, msg_ok
)


class DialogoEstudiante(DialogoBase):
    def __init__(self, estudiante=None, parent=None):
        titulo = "Registrar Estudiante" if not estudiante else "Editar Estudiante"
        super().__init__(titulo, parent)

        self.txt_nombre  = self._campo_texto("Nombre")
        self.txt_apellido= self._campo_texto("Apellido")
        self.txt_correo  = self._campo_texto("correo@ucuenca.edu.ec")
        self.txt_tel     = self._campo_texto("09XXXXXXXX")
        self.spn_ciclo   = self._campo_spin(1, 10, 1)
        self.txt_malla   = self._campo_texto("Ej. Computación 2021")
        self.txt_cv      = self._campo_texto("Ruta o descripción del CV")
        self.chk_previa  = self._campo_check("Ya realizó prácticas anteriormente")

        self._agregar_campo("Nombre *",          self.txt_nombre,  True)
        self._agregar_campo("Apellido *",         self.txt_apellido,True)
        self._agregar_campo("Correo *",           self.txt_correo,  True)
        self._agregar_campo("Teléfono",           self.txt_tel)
        self._agregar_campo("Ciclo *",            self.spn_ciclo,   True)
        self._agregar_campo("Malla",              self.txt_malla)
        self._agregar_campo("CV",                 self.txt_cv)
        self._agregar_campo("Práctica Previa",    self.chk_previa)

        if estudiante:
            self.txt_nombre.setText(estudiante.nombre)
            self.txt_apellido.setText(estudiante.apellido)
            self.txt_correo.setText(estudiante.correo)
            self.txt_tel.setText(estudiante.telefono)
            self.spn_ciclo.setValue(estudiante.ciclo)
            self.txt_malla.setText(estudiante.malla)
            self.txt_cv.setText(estudiante.CV)
            self.chk_previa.setChecked(estudiante.tiene_practica_previa)

    def datos(self):
        return (
            self.txt_nombre.text(),
            self.txt_apellido.text(),
            self.txt_correo.text(),
            self.txt_tel.text(),
            self.spn_ciclo.value(),
            self.txt_malla.text(),
            self.txt_cv.text(),
            self.chk_previa.isChecked(),
        )


class EstudianteVista(SeccionBase):
    def __init__(self, ctrl, parent=None):
        self.ctrl = ctrl
        super().__init__("👩‍🎓  Estudiantes", parent)

    def _headers(self):
        return ["ID", "Nombre", "Apellido", "Correo", "Ciclo", "Práctica Previa", "Puede Externas"]

    def _cargar_filas(self):
        filas = []
        for e in self.ctrl.listar():
            filas.append([
                e.id_estudiante,
                e.nombre,
                e.apellido,
                e.correo,
                e.ciclo,
                "Sí" if e.tiene_practica_previa else "No",
                "✔" if e.puede_practicas_externas() else "✗",
            ])
        return filas

    def _on_agregar(self):
        dlg = DialogoEstudiante(parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.agregar(*dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_editar(self, id_):
        e = self.ctrl.obtener(id_)
        if not e: return
        dlg = DialogoEstudiante(estudiante=e, parent=self)
        if dlg.exec() == DialogoBase.DialogCode.Accepted:
            ok, msg = self.ctrl.actualizar(id_, *dlg.datos())
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()

    def _on_eliminar(self, id_):
        e = self.ctrl.obtener(id_)
        if e and confirmar_eliminacion(self, f"al estudiante '{e.nombre_completo}'"):
            ok, msg = self.ctrl.eliminar(id_)
            (msg_ok if ok else msg_error)(self, msg)
            if ok: self.actualizar()
