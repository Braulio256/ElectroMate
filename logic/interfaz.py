import sys

# --- CONFIGURACIÓN VISUAL ---
C_BOT = "\033[94m[ELECTROMATE]>\033[0m"
C_USR = "\033[92m[TU] >\033[0m"
C_SYS = "\033[93m[SISTEMA]>\033[0m"


class CambioDeContexto(Exception):
    def __init__(self, nuevo_comando):
        self.nuevo_comando = nuevo_comando


def input_profesional(mensaje_bot, tipo_dato=float):
    """
    Gestiona la entrada del usuario, valida tipos y detecta comandos de salida.
    """
    print(f"{C_BOT} {mensaje_bot}")
    entrada = input(f"{C_USR} ").strip()

    comandos_cancelacion = ["cancelar", "salir", "menu", "atras", "basta"]
    palabras_clave_nuevas = ["diseña", "calcula", "filtro", "resistencia", "ley de ohm", "quiero"]

    # Detección de cancelación
    if entrada.lower() in comandos_cancelacion:
        raise CambioDeContexto("cancelar")

    # Detección de cambio de tema
    if len(entrada.split()) > 1 and any(p in entrada.lower() for p in palabras_clave_nuevas):
        raise CambioDeContexto(entrada)

    # Conversión de datos
    if tipo_dato == float:
        multiplicador = 1
        clean_input = entrada.lower()
        if clean_input.endswith('k'):
            multiplicador = 1e3; clean_input = clean_input[:-1]
        elif clean_input.endswith('m'):
            multiplicador = 1e-3; clean_input = clean_input[:-1]
        elif clean_input.endswith('u'):
            multiplicador = 1e-6; clean_input = clean_input[:-1]

        try:
            val = float(clean_input) * multiplicador
            if val < 0:
                print(f"{C_SYS} Advertencia: Valor negativo detectado.")
            return val
        except ValueError:
            print(f"{C_SYS} Error de formato: Se esperaba un número. Inténtalo de nuevo.")
            return input_profesional(mensaje_bot, tipo_dato)

    return entrada