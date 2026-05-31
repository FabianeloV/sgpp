"""
main.py
Punto de entrada – SGPP Sistema de Gestión de Prácticas Pre-Profesionales
Universidad de Cuenca – Carrera de Computación  |  2026
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar el controlador principal (Ajusta 'controladores' al nombre real de tu paquete)
from controlador.controlador_principal import ControladorPrincipal


def main():
    """
    Función principal de arranque.
    Delega toda la responsabilidad de inicialización y ejecución al ControladorPrincipal.
    """
    controlador = ControladorPrincipal()
    sys.exit(controlador.ejecutar())


if __name__ == "__main__":
    main()