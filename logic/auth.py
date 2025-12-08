import json
import os
import hashlib
import time
import re
from logic.interfaz import C_BOT, C_USR, C_SYS, input_profesional


class GestorSesion:
    def __init__(self):
        self.archivo_db = os.path.join("data", "users.json")
        self.usuarios = self._cargar_usuarios()
        self.usuario_actual = None

    def _cargar_usuarios(self):
        try:
            with open(self.archivo_db, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _guardar_usuarios(self):
        with open(self.archivo_db, 'w', encoding='utf-8') as f:
            json.dump(self.usuarios, f, indent=2)

    def _hashear_password(self, password):
        """Cifra solo la contraseña"""
        return hashlib.sha256(password.strip().encode()).hexdigest()

    def _es_email_valido(self, email):
        patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(patron, email) is not None

    def registrar_usuario(self):
        print(f"\n{C_BOT} --- REGISTRO DE NUEVO USUARIO ---")

        username = input(f"       Nombre de usuario: {C_USR}").strip()
        if not username:
            print(f"{C_SYS} El usuario no puede estar vacío.")
            return False

        # Verificar duplicados de usuario
        for u in self.usuarios:
            if u['username'].lower() == username.lower():
                print(f"{C_SYS} Error: El usuario '{username}' ya existe.")
                return False

        email = input(f"       Correo electrónico: {C_USR}").strip()
        if not self._es_email_valido(email):
            print(f"{C_SYS} Error: Formato de correo inválido.")
            return False

        # Verificar duplicados de correo (Ahora comparamos texto plano)
        for u in self.usuarios:
            if u.get('email', '').lower() == email.lower():
                print(f"{C_SYS} Error: Ese correo ya está registrado.")
                return False

        password = input(f"       Contraseña: {C_USR}").strip()
        if len(password) < 4:
            print(f"{C_SYS} Error: La contraseña es muy corta (min 4 caracteres).")
            return False

        confirm_password = input(f"       Confirmar contraseña: {C_USR}").strip()
        if password != confirm_password:
            print(f"{C_SYS} Error: Las contraseñas NO coinciden.")
            return False

        # Guardamos: Usuario (plano), Email (plano), Password (HASH)
        nuevo_usuario = {
            "username": username,
            "email": email,  # GUARDADO SIN HASHEAR
            "password_hash": self._hashear_password(password),
            "fecha_registro": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        self.usuarios.append(nuevo_usuario)
        self._guardar_usuarios()
        print(f"{C_BOT} ¡Cuenta creada exitosamente! Por favor inicia sesión.")
        return True

    def recuperar_contrasena(self):
        print(f"\n{C_BOT} --- RECUPERACIÓN DE CUENTA ---")
        print(f"{C_SYS} Para restablecer, necesitamos verificar tu identidad.")

        user_input = input(f"       Nombre de usuario: {C_USR}").strip()
        email_input = input(f"       Correo registrado: {C_USR}").strip()

        usuario_encontrado = None

        # Buscamos coincidencia exacta de Usuario Y Correo
        for u in self.usuarios:
            if (u['username'].lower() == user_input.lower()) and \
                    (u.get('email', '').lower() == email_input.lower()):
                usuario_encontrado = u
                break

        if not usuario_encontrado:
            print(f"{C_SYS} Error: No coinciden los datos o el usuario no existe.")
            return False

        print(f"{C_BOT} Identidad verificada. Proceda a cambiar su clave.")

        nueva_pass = input(f"       Nueva contraseña: {C_USR}").strip()
        if len(nueva_pass) < 4:
            print(f"{C_SYS} Contraseña muy corta.")
            return False

        confirm_pass = input(f"       Confirmar nueva contraseña: {C_USR}").strip()
        if nueva_pass != confirm_pass:
            print(f"{C_SYS} Las contraseñas no coinciden. Operación cancelada.")
            return False

        # Si está bien, actualizamos el hash y guardamos
        usuario_encontrado['password_hash'] = self._hashear_password(nueva_pass)
        self._guardar_usuarios()

        print(f"{C_BOT} ¡Contraseña actualizada! Vuelve a iniciar sesión.")
        return True

    def iniciar_sesion(self):
        print(f"\n{C_BOT} --- INICIAR SESIÓN ---")
        username = input(f"       Usuario: {C_USR}").strip()
        password = input(f"       Contraseña: {C_USR}").strip()

        hash_pass_input = self._hashear_password(password)

        usuario_detectado = None
        for user in self.usuarios:
            if user['username'].lower() == username.lower():
                usuario_detectado = user
                break

        # Caso 1: Usuario no existe
        if not usuario_detectado:
            print(f"{C_SYS} Usuario no encontrado.")
            return False

        # Caso 2: Usuario existe, verificamos contraseña
        if usuario_detectado['password_hash'] == hash_pass_input:
            self.usuario_actual = usuario_detectado['username']
            print(f"{C_BOT} Credenciales correctas. Bienvenido, {usuario_detectado['username']}.")
            return True
        else:
            # Caso 3: Contraseña incorrecta -> Flujo de recuperación
            print(f"{C_SYS} Contraseña incorrecta.")

            # Pregunta clave
            print(f"{C_BOT} ¿Olvidaste tu contraseña?")
            resp = input(f"       (si/no): {C_USR}").lower()

            if resp in ["si", "s", "yes", "y"]:
                self.recuperar_contrasena()
                # Retornamos False para que el bucle del menú principal lo obligue a loguearse de nuevo
                # con la contraseña nueva, en lugar de entrar directo.
                return False
            else:
                print(f"{C_BOT} Regresando al menú de inicio...")
                return False

    def menu_autenticacion(self):
        while True:
            print("\n" + "=" * 40)
            print("      ELECTROMATE v5.0 - SEGURIDAD      ")
            print("=" * 40)
            print(" [1] Iniciar Sesión")
            print(" [2] Crear Cuenta")
            print(" [3] Salir")

            opcion = input(f"\n{C_USR} ").strip()

            if opcion == "1":
                if self.iniciar_sesion():
                    return True
            elif opcion == "2":
                self.registrar_usuario()
            elif opcion == "3":
                print(f"{C_SYS} Cerrando sistema...")
                return False
            else:
                print(f"{C_SYS} Opción no válida.")