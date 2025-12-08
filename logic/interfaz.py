import sys
import re

# --- CONFIGURACIÓN VISUAL ---
C_BOT = "\033[94m[ELECTROMATE]>\033[0m"
C_USR = "\033[92m[TU] >\033[0m"
C_SYS = "\033[93m[SISTEMA]>\033[0m"

# --- BASE DE DATOS DE SUFIJOS ---
SUFIJOS = {
    'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'µ': 1e-6,
    'm': 1e-3, 'k': 1e3, 'M': 1e6, 'g': 1e9, 'G': 1e9
}


class CambioDeContexto(Exception):
    def __init__(self, nuevo_comando):
        self.nuevo_comando = nuevo_comando


def parsear_valor(texto):
    """Convierte '1.2k' a 1200.0"""
    if not texto: return None
    texto = texto.strip().replace(",", ".")

    # Regex robusto: Captura número y sufijo (ignorando unidades como Hz, Ohm, F si están pegadas)
    match = re.match(r"^([0-9\.]+)\s*([a-zA-Zµ]*)", texto)
    if not match: return None

    numero_str = match.group(1)
    sufijo_str = match.group(2)

    try:
        valor = float(numero_str)
    except ValueError:
        return None

    # Detectar multiplicador en la primera letra del sufijo
    multiplicador = 1.0
    if sufijo_str:
        primera_letra = sufijo_str[0]
        # Caso especial: 'm' puede ser mili, pero 'M' es Mega.
        # Si el usuario escribe 'meg' o 'M', es Mega.
        if primera_letra == 'M' or "meg" in sufijo_str.lower():
            multiplicador = 1e6
        elif primera_letra in SUFIJOS:
            multiplicador = SUFIJOS[primera_letra]

    return valor * multiplicador


def formatear_valor(valor, unidad=""):
    """
    Formato inteligente: 1001670 -> 1.002 M
    Usa 3 decimales para no perder detalles pequeños.
    """
    if valor == 0: return f"0 {unidad}"
    abs_val = abs(valor)

    sufijo = ""
    divisor = 1.0

    if abs_val >= 1e9:
        sufijo = "G"; divisor = 1e9
    elif abs_val >= 1e6:
        sufijo = "M"; divisor = 1e6
    elif abs_val >= 1e3:
        sufijo = "k"; divisor = 1e3
    elif abs_val >= 1:
        sufijo = ""; divisor = 1
    elif abs_val >= 1e-3:
        sufijo = "m"; divisor = 1e-3
    elif abs_val >= 1e-6:
        sufijo = "u"; divisor = 1e-6
    elif abs_val >= 1e-9:
        sufijo = "n"; divisor = 1e-9
    else:
        sufijo = "p"; divisor = 1e-12

    val_formateado = valor / divisor

    # Formatear a 3 decimales y quitar ceros a la derecha (1.500 -> 1.5)
    texto_num = f"{val_formateado:.4f}".rstrip('0').rstrip('.')

    return f"{texto_num} {sufijo}{unidad}"


def input_profesional(mensaje_bot, tipo_dato=float):
    print(f"{C_BOT} {mensaje_bot}")
    entrada = input(f"{C_USR} ").strip()

    comandos_cancelacion = ["cancelar", "salir", "menu", "atras", "basta"]
    palabras_clave_nuevas = ["diseña", "calcula", "filtro", "resistencia", "ley de ohm", "quiero"]

    if entrada.lower() in comandos_cancelacion:
        raise CambioDeContexto("cancelar")

    if len(entrada.split()) > 1 and any(p in entrada.lower() for p in palabras_clave_nuevas):
        raise CambioDeContexto(entrada)

    if tipo_dato == float:
        val = parsear_valor(entrada)
        if val is None:
            print(f"{C_SYS} Error: '{entrada}' no es válido. Intenta ej: '10k', '0.5', '1M'.")
            return input_profesional(mensaje_bot, tipo_dato)
        return val

    return entrada