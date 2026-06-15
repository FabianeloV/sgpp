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

## Arquitectura (MVC)
El sistema sigue el patrón **Modelo–Vista–Controlador**, repartido así:

| Capa | Cantidad |
|------|----------|
| **Modelos** — entidades de dominio (`modelo/`) | **16** |
| **Controladores** (`controlador/`) | **13** |
| **Vistas / pantallas** (`vista/`) | **15** |

Detalle:

- **16 modelos** (entidades `@dataclass`): Empresa, Convenio, OfertaPractica, Tutor,
  TutorAcademico, TutorEmpresarial, Coordinador, Estudiante, Postulacion, Terna, Practica,
  Actividad, Formulario, Documento, SolicitudAutorizacion, Usuario.
  *(El paquete `modelo/` tiene 26 clases en total: estas 16 entidades + 8 enumeraciones de
  estado/tipo + Repositorio y Sesión.)*
- **13 controladores**: Principal (orquestador) + Empresa, Convenio, Oferta, Tutor, Coordinador,
  Estudiante, Postulacion, Terna, Practica, Solicitud, Usuario, Reporte.
- **15 vistas**: MainWindow + Dashboard, Estudiantes, Empresas, Ofertas, Postulaciones, Ternas,
  Prácticas, Tutores (Académicos y Empresariales), Coordinadores, Solicitudes, Usuarios, Reportes.
  *(El paquete `vista/` tiene 45 clases en total: estas 15 vistas + 25 diálogos + 5 widgets
  reutilizables.)*

## Acceso (Login y roles)
Al iniciar, la app pide **usuario y contraseña**. Cada usuario tiene un **rol** que determina
qué secciones del menú ve y qué datos puede gestionar (cada empresa/estudiante solo ve lo suyo).
Botón **"Cerrar sesión"** en la cabecera para cambiar de usuario.

### Primer uso
La aplicación **no incluye datos de ejemplo**. La primera vez que se ejecuta —o si se borra el
archivo de datos `data/sgpp_data.pkl`— al arrancar pide **crear la cuenta de administrador**
(usted elige el usuario y la contraseña). Con esa cuenta inicia sesión y, desde la sección
**Usuarios**, crea las demás cuentas. El sistema **no genera datos por su cuenta**.

### Roles y qué puede hacer cada uno

| Rol           | Acceso |
|---------------|--------|
| Administrador | Todo el sistema (incluida la gestión de **Usuarios**) |
| Coordinador   | Dashboard, Estudiantes, Postulaciones, Ternas, Prácticas, Tutores, Solicitudes, Reportes |
| Empresa       | Dashboard, **sus** Ofertas, **sus** Ternas, **sus** Tutores empresariales |
| Tutor         | Dashboard, Estudiantes, Postulaciones, Ternas (genera y procesa postulaciones) |
| Estudiante    | Ofertas activas (solo lectura) |

El **Administrador** puede crear, editar y eliminar usuarios desde la sección **Usuarios**
(visible solo para él), eligiendo el rol y la entidad a la que se vincula el usuario.

### Crear usuarios: primero la entidad, luego el usuario
Salvo el Administrador, **cada usuario representa a una entidad ya registrada** en el sistema
(una empresa, un estudiante, etc.). Por eso, para crear el usuario de un rol, primero debe
existir su entidad en la sección correspondiente:

| Para un usuario de rol… | Primero registre…    | En la sección…  |
|-------------------------|----------------------|-----------------|
| Empresa                 | la empresa           | Empresas        |
| Estudiante              | el estudiante        | Estudiantes     |
| Tutor                   | el tutor académico   | Tutores         |
| Coordinador             | el coordinador       | Coordinadores   |
| Administrador           | (nada que registrar) | —               |

**Ejemplo — dar acceso a una empresa:**
1. Inicie sesión como **Administrador**.
2. Vaya a **Empresas → Agregar** y registre, por ejemplo, «Etapa EP».
3. Vaya a **Usuarios → Agregar**, escriba el usuario y la contraseña, elija el rol **Empresa**
   y, en *Vinculado a*, seleccione «Etapa EP».
4. Al iniciar sesión, esa cuenta verá y gestionará únicamente lo de «Etapa EP».

**Ejemplo — dar acceso a un estudiante:** primero **Estudiantes → Agregar** (p. ej. «Ana Torres»),
y luego **Usuarios → Agregar** con rol **Estudiante** vinculado a «Ana Torres».

> Alternativa: puede crear el usuario con *Vinculado a* en **«— Sin vincular —»** y asociarlo a su
> entidad más tarde con **Editar**. Un usuario sin vincular podrá iniciar sesión, pero no verá
> "sus" datos hasta que se le asigne una entidad.

El **Administrador** y el **Coordinador** pueden **exportar reportes en PDF** desde la sección
**Reportes**: un resumen general (los mismos datos del dashboard) y listados de estudiantes,
prácticas y postulaciones.

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
