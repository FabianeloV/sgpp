from typing import Optional, Tuple

from modelo.entidades import Usuario, RolUsuario
from modelo.repositorio import Repositorio


class ControladorUsuario:
    def __init__(self): self.repo = Repositorio()

    def _validar_ref(self, rol: str, ref_id) -> Tuple[bool, str]:
        """Si se indica un ref_id, verifica que exista en la colección del rol.

        El vínculo es OPCIONAL: un usuario puede crearse "sin vincular" y asociarse a
        su entidad más tarde. Solo se valida que, de indicarse, el ref_id sea válido
        (evita vínculos a entidades inexistentes).
        """
        if rol == RolUsuario.ADMINISTRADOR or not ref_id:
            return True, ""
        buscar = {
            RolUsuario.COORDINADOR: self.repo.obtener_coordinador,
            RolUsuario.EMPRESA:     self.repo.obtener_empresa,
            RolUsuario.TUTOR:       self.repo.obtener_t_academico,
            RolUsuario.ESTUDIANTE:  self.repo.obtener_estudiante,
        }.get(rol)
        if buscar and buscar(ref_id) is None:
            return False, "La entidad vinculada (ref_id) no existe."
        return True, ""

    def agregar(self, nombre: str, password: str, rol: str,
                ref_id: Optional[str] = None) -> Tuple[bool, str]:
        nombre = nombre.strip()
        if not nombre: return False, "Nombre de usuario requerido."
        if not password: return False, "Contraseña requerida."
        if rol not in RolUsuario.TODOS: return False, "Rol inválido."
        ok_ref, msg_ref = self._validar_ref(rol, ref_id)
        if not ok_ref: return False, msg_ref
        if self.repo.obtener_usuario_por_nombre(nombre):
            return False, "Ya existe un usuario con ese nombre."
        u = Usuario(nombre=nombre, password=password, rol=rol, ref_id=ref_id)
        self.repo.agregar_usuario(u)
        return True, f"Usuario registrado (ID: {u.id_usuario})."

    def actualizar(self, id_: str, nombre: str, password: str, rol: str,
                   ref_id: Optional[str] = None) -> Tuple[bool, str]:
        u = self.repo.obtener_usuario(id_)
        if not u: return False, "Usuario no encontrado."
        nombre = nombre.strip()
        if not nombre: return False, "Nombre de usuario requerido."
        if not password: return False, "Contraseña requerida."
        if rol not in RolUsuario.TODOS: return False, "Rol inválido."
        ok_ref, msg_ref = self._validar_ref(rol, ref_id)
        if not ok_ref: return False, msg_ref
        otro = self.repo.obtener_usuario_por_nombre(nombre)
        if otro and otro.id_usuario != id_:
            return False, "Ya existe un usuario con ese nombre."
        u.nombre, u.password, u.rol, u.ref_id = nombre, password, rol, ref_id
        self.repo.actualizar_usuario(u)
        return True, "Usuario actualizado."

    def eliminar(self, id_: str) -> Tuple[bool, str]:
        self.repo.eliminar_usuario(id_)
        return True, "Usuario eliminado."

    def listar(self):                     return self.repo.listar_usuarios()
    def obtener(self, id_):               return self.repo.obtener_usuario(id_)
    def obtener_por_nombre(self, nombre): return self.repo.obtener_usuario_por_nombre(nombre)

    def autenticar(self, nombre: str, password: str) -> Optional[Usuario]:
        return self.repo.autenticar(nombre.strip(), password)
