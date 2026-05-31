# SGPP – Sistema de Gestión de Prácticas Pre-Profesionales
**Universidad de Cuenca – Carrera de Computación | Bases de Datos I · 2026**

## Requisitos
```
pip install PyQt6
```

## Ejecutar
```
cd sgpp/
python main.py
```

## Arquitectura MVC
```
sgpp/
├── main.py                        # Punto de entrada
├── modelo/
│   ├── entidades.py               # Dataclasses del dominio
│   └── repositorio.py             # Singleton Pickle – toda la persistencia
├── controlador/
│   └── controladores.py           # Lógica de negocio y validaciones
└── vista/
    ├── widgets.py                 # Componentes reutilizables / estilos
    ├── main_window.py             # Ventana principal + sidebar
    ├── dashboard_vista.py         # Panel resumen con estadísticas
    ├── empresa_vista.py           # CRUD Empresa + Convenios
    ├── estudiante_vista.py        # CRUD Estudiante
    ├── oferta_vista.py            # CRUD Oferta de Práctica
    ├── postulacion_vista.py       # Postulaciones + Ternas
    ├── practica_vista.py          # Prácticas + Actividades + Formularios
    ├── tutor_vista.py             # Tutores Académicos/Empresariales + Coordinadores
    └── solicitud_vista.py         # Solicitudes de Autorización
```

## Flujo principal
1. Registrar **Empresa** → agregar **Convenio** (si aplica)
2. Publicar **Oferta de Práctica** (la empresa)
3. Registrar **Estudiante** (≥ 6.° ciclo para prácticas externas)
4. Crear **Postulación** (estudiante → oferta)
5. **Validar** postulación (Coordinador revisa malla + CV)
6. Agregar postulaciones validadas a una **Terna** (máx. 3 por oferta)
7. **Enviar terna** a la empresa → empresa **Acepta** una postulación
8. Crear **Práctica** (asignar tutor académico + empresarial) → se genera Formulario 1
9. Registrar **Actividades** → tutor académico las valida
10. **Finalizar** práctica → completar Formularios 2 y 3
11. **Aprobar** oficialmente (Coordinador) → estudiante queda marcado con práctica previa
