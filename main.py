import sys
import math
from logic.buscador import BuscadorComponentes
from logic.procesador import ProcesadorTexto
from logic.calculos import (
    calcular_resistencia_limitadora,
    calcular_corriente_ohm,
    calcular_voltaje_ohm,
    calcular_resistencia_ohm,
    calcular_potencia_dc,
    calcular_par_rc,
    calcular_par_rl,
    calcular_par_rlc,
    calcular_ganancia_opamp
)

# --- CONFIGURACIÓN DE INTERFAZ ---
C_BOT = "\033[94m[ELECTROMATE]>\033[0m"
C_USR = "\033[92m[TU] >\033[0m"
C_SYS = "\033[93m[SISTEMA]>\033[0m"


class CambioDeContexto(Exception):
    def __init__(self, nuevo_comando):
        self.nuevo_comando = nuevo_comando


def input_profesional(mensaje_bot, tipo_dato=float):
    """Gestiona entrada, detecta comandos y limpia datos."""
    print(f"{C_BOT} {mensaje_bot}")
    entrada = input(f"{C_USR} ").strip()

    comandos_cancelacion = ["cancelar", "salir", "menu", "atras", "basta"]
    palabras_clave_nuevas = ["diseña", "calcula", "filtro", "resistencia", "ley de ohm", "quiero"]

    # 1. Chequeo de cancelación
    if entrada.lower() in comandos_cancelacion:
        raise CambioDeContexto("cancelar")

    # 2. Chequeo de cambio de tema (si escribe una frase larga de comando)
    if len(entrada.split()) > 1 and any(p in entrada.lower() for p in palabras_clave_nuevas):
        raise CambioDeContexto(entrada)

    # 3. Procesamiento de dato numérico
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
            return float(clean_input) * multiplicador
        except ValueError:
            print(f"{C_SYS} Error de formato: Se esperaba un valor numérico.")
            return input_profesional(mensaje_bot, tipo_dato)

    return entrada


def main():
    print("=====================================================")
    print("      ELECTROMATE v3.7 - ASISTENTE DE INGENIERÍA     ")
    print("=====================================================")
    print("Sistema listo. Puedes hablarme naturalmente.")
    print("Ejemplos: 'Filtro activo pasa bajas', 'Resistencia led', 'Calcula potencia'.")

    motor = BuscadorComponentes()
    procesador = ProcesadorTexto()
    comando_pendiente = None

    while True:
        try:
            if comando_pendiente:
                entrada = comando_pendiente
                comando_pendiente = None
                print(f"{C_SYS} Redirigiendo solicitud: '{entrada}'")
            else:
                entrada = input(f"\n{C_USR} ")

            if entrada.lower() in ["salir", "exit", "shutdown"]:
                print(f"{C_BOT} Finalizando sesión. Guardando registros... Apagado.")
                break

            intencion = procesador.identificar_intencion(entrada)
            datos = procesador.extraer_parametros(entrada)

            try:
                ejecutar_tarea(intencion, datos, motor)
            except CambioDeContexto as e:
                if e.nuevo_comando == "cancelar":
                    print(f"{C_SYS} Operación abortada por el usuario.")
                else:
                    print(f"{C_SYS} Interrupción detectada. Cambiando de tarea...")
                    comando_pendiente = e.nuevo_comando

        except Exception as e:
            print(f"{C_SYS} Excepción no controlada: {e}")


def ejecutar_tarea(intencion, datos, motor):
    # Enrutador principal
    if intencion == "FILTRO_AMBIGUO":
        resolver_filtro_ambiguo()
    elif intencion == "FILTRO_ACTIVO":
        resolver_filtro_activo(datos, motor)
    elif intencion == "FILTRO_RL":
        resolver_filtro_rl(datos, motor)
    elif intencion == "FILTRO_RLC":
        resolver_filtro_rlc(datos, motor)

    elif intencion in ["FILTRO_LP", "FILTRO_HP", "FILTRO_NOTCH"]:
        tipo = intencion.replace("FILTRO_", "")
        resolver_filtro_rc(datos, motor, tipo)

    elif intencion == "FILTRO_CALC_FC_RC":
        resolver_calc_fc_rc(datos)
    elif intencion == "OHM_CALC_V":
        resolver_voltaje(datos, motor)
    elif intencion == "OHM_CALC_I":
        resolver_corriente(datos, motor)
    elif intencion == "OHM_CALC_R":
        resolver_resistencia(datos, motor)
    elif intencion == "OHM_CALC_P":
        resolver_potencia(datos, motor)
    elif intencion == "OHM_LED":
        resolver_led(datos, motor)
    else:
        print(f"{C_BOT} Solicitud no reconocida.")
        print("       Intente: 'Diseñar filtro activo', 'Calcula resistencia LED', 'Ley de Ohm'.")


# --- RESOLVEDORES DE FILTROS (MENUS MEJORADOS) ---

def resolver_filtro_ambiguo():
    print(f"{C_BOT} Solicitud ambigua. Seleccione la tecnología del filtro:")
    print("       [1] Pasivo RC (Resistencia-Capacitor - Señal)")
    print("       [2] Activo (Op-Amps - Audio/Instrumentación)")
    print("       [3] Inductivo RL (Bobinas - Potencia)")
    print("       [4] Resonante RLC (Tanque - Radiofrecuencia)")

    resp = input_profesional("Ingrese número (1-4) o nombre:", str).lower()

    # Lógica híbrida: Número O Texto
    if "2" in resp or "activo" in resp or "opamp" in resp:
        raise CambioDeContexto("diseñar filtro activo")

    elif "4" in resp or "rlc" in resp or "resonante" in resp:
        raise CambioDeContexto("diseñar filtro rlc")

    elif "3" in resp or "rl" in resp or "inductivo" in resp:
        raise CambioDeContexto("diseñar filtro rl")

    elif "1" in resp or "rc" in resp or "pasivo" in resp:
        # Sub-menú explícito para RC
        print(f"{C_BOT} Configuración RC Pasiva. Seleccione respuesta:")
        print("       [1] Pasa Bajas (Low Pass)")
        print("       [2] Pasa Altas (High Pass)")
        print("       [3] Rechaza Banda (Notch)")

        sub_resp = input_profesional("Opción:", str).lower()

        if "1" in sub_resp or "baja" in sub_resp or "lp" in sub_resp: raise CambioDeContexto(
            "diseñar filtro pasa bajas")
        if "2" in sub_resp or "alta" in sub_resp or "hp" in sub_resp: raise CambioDeContexto(
            "diseñar filtro pasa altas")
        if "3" in sub_resp or "rechaza" in sub_resp or "notch" in sub_resp: raise CambioDeContexto(
            "diseñar filtro notch")

        print(f"{C_SYS} Opción no válida. Reiniciando selección.")

    else:
        print(f"{C_SYS} Opción no válida.")


def resolver_filtro_activo(datos, motor):
    print(f"{C_BOT} Diseño de Filtro ACTIVO (Op-Amp).")

    # Menú numérico + texto
    print(f"{C_BOT} Seleccione la respuesta en frecuencia:")
    print("       [1] Pasa Bajas (Low Pass)")
    print("       [2] Pasa Altas (High Pass)")
    print("       [3] Pasa Banda (Band Pass)")
    print("       [4] Rechaza Banda (Notch)")

    resp = input_profesional("Opción:", str).lower()

    tipo = "LP"  # Default
    if "2" in resp or "alta" in resp or "hp" in resp:
        tipo = "HP"
    elif "3" in resp or "banda" in resp or "bp" in resp:
        tipo = "BP"
    elif "4" in resp or "rechaza" in resp or "notch" in resp:
        tipo = "NOTCH"
    elif "1" in resp or "baja" in resp or "lp" in resp:
        tipo = "LP"

    # Lógica Pasa Banda (requiere 2 frecuencias)
    if tipo == "BP":
        fb = input_profesional("Frecuencia de Corte Inferior (fL):")
        fa = input_profesional("Frecuencia de Corte Superior (fH):")
        v = input_profesional("Voltaje de alimentación (V):")

        hp = calcular_par_rc(motor, fb, v)
        lp = calcular_par_rc(motor, fa, v, "bajo")
        opamp, _ = motor.buscar_opamp_apto(fa, v)

        if hp and lp and opamp:
            print(f"{C_BOT} Diseño BP Activo Generado:")
            print(f"       [OpAmp] {opamp['nombre']}")
            print(f"       [Etapa HP] C={hp['c']['nombre']}, R={hp['r']['nombre']}")
            print(f"       [Etapa LP] R={lp['r']['nombre']}, C={lp['c']['nombre']}")
        else:
            print(f"{C_SYS} Error de cálculo en componentes.")
        return

    # Lógica Estándar (1 frecuencia)
    f = datos.get('frecuencia')
    if f is None: f = input_profesional("Frecuencia de Corte (Hz):")
    v = datos.get('voltaje')
    if v is None: v = input_profesional("Voltaje de alimentación (V):")

    res = calcular_par_rc(motor, f, v)
    opamp, _ = motor.buscar_opamp_apto(f, v)

    if res and opamp:
        print(f"{C_BOT} Diseño {tipo} Activo Generado:")
        print(f"       [OpAmp] {opamp['nombre']}")
        if tipo == "LP":
            print(f"       [Red RC] R={res['r']['nombre']} (Serie), C={res['c']['nombre']} (Gnd)")
        elif tipo == "HP":
            print(f"       [Red RC] C={res['c']['nombre']} (Serie), R={res['r']['nombre']} (Gnd)")
        elif tipo == "NOTCH":
            print(f"       [Twin-T] R={res['r']['nombre']}, C={res['c']['nombre']}")
    else:
        print(f"{C_SYS} No se encontraron componentes adecuados.")


def resolver_filtro_rc(datos, motor, tipo):
    nombres = {"LP": "Pasa Bajas", "HP": "Pasa Altas", "NOTCH": "Rechaza Banda"}
    print(f"{C_BOT} Diseño Filtro Pasivo RC - {nombres.get(tipo)}.")

    f = datos.get('frecuencia')
    if f is None: f = input_profesional("Frecuencia de Corte (Hz):")
    v = datos.get('voltaje', 5.0)

    res = calcular_par_rc(motor, f, v)
    if res:
        print(f"{C_BOT} Componentes Calculados (F={res['f']:.1f}Hz):")
        print(f"       • R: {res['r']['nombre']}")
        print(f"       • C: {res['c']['nombre']}")
    else:
        print(f"{C_SYS} Sin resultados comerciales.")


def resolver_filtro_rl(datos, motor):
    print(f"{C_BOT} Diseño Filtro RL (Inductivo).")
    f = input_profesional("Frecuencia de Corte (Hz):")
    i = input_profesional("Corriente Máxima (A):")
    res = calcular_par_rl(motor, f, i)
    if res:
        print(f"{C_BOT} Componentes Calculados:")
        print(f"       • L: {res['l']['nombre']}")
        print(f"       • R: {res['r']['nombre']}")
    else:
        print(f"{C_SYS} No hay inductores adecuados.")


def resolver_filtro_rlc(datos, motor):
    print(f"{C_BOT} Diseño Filtro RLC (Resonante).")
    f = input_profesional("Frecuencia Resonancia (Hz):")
    res = calcular_par_rlc(motor, f, 5.0)
    if res:
        print(f"{C_BOT} Tanque LC:")
        print(f"       • L: {res['l']['nombre']}")
        print(f"       • C: {res['c']['nombre']}")
    else:
        print(f"{C_SYS} No hay componentes adecuados.")


def resolver_calc_fc_rc(datos):
    print(f"{C_BOT} Calculadora Frecuencia de Corte RC.")
    r = input_profesional("Resistencia (Ω):")
    c = input_profesional("Capacitor (uF):") / 1e6
    fc = 1 / (2 * math.pi * r * c)
    print(f"{C_BOT} Frecuencia: {fc:.2f} Hz")


# --- RESOLVEDORES OHM ---
def resolver_voltaje(d, m):
    print(f"{C_BOT} Cálculo V = I * R")
    i = input_profesional("Corriente (mA):") / 1000
    r = input_profesional("Resistencia (Ω):")
    v = calcular_voltaje_ohm(i, r);
    p = calcular_potencia_dc(v, i)
    print(f"{C_BOT} V: {v:.2f}V | P: {p:.3f}W")
    c, _ = m.buscar_resistencia_optima(r, p)
    if c: print(f"       ✅ {c['nombre']}")


def resolver_corriente(d, m):
    print(f"{C_BOT} Cálculo I = V / R")
    v = input_profesional("Voltaje (V):")
    r = input_profesional("Resistencia (Ω):")
    i = calcular_corriente_ohm(v, r);
    p = calcular_potencia_dc(v, i)
    print(f"{C_BOT} I: {i * 1000:.1f}mA | P: {p:.3f}W")
    c, _ = m.buscar_resistencia_optima(r, p)
    if c: print(f"       ✅ {c['nombre']}")


def resolver_resistencia(d, m):
    print(f"{C_BOT} Cálculo R = V / I")
    v = input_profesional("Voltaje (V):")
    i = input_profesional("Corriente (mA):") / 1000
    r = calcular_resistencia_ohm(v, i);
    p = calcular_potencia_dc(v, i)
    print(f"{C_BOT} R: {r:.2f}Ω")
    c, _ = m.buscar_resistencia_optima(r, p)
    if c: print(f"       ✅ {c['nombre']}")


def resolver_potencia(d, m):
    print(f"{C_BOT} Cálculo P = V * I")
    v = input_profesional("Voltaje (V):")
    i = input_profesional("Corriente (mA):") / 1000
    p = calcular_potencia_dc(v, i)
    print(f"{C_BOT} Potencia: {p:.4f}W")


def resolver_led(d, m):
    print(f"{C_BOT} Cálculo R Limitadora LED")
    v = input_profesional("V Fuente:")
    vl = input_profesional("V LED:")
    i = input_profesional("I LED (mA):") / 1000
    r, p = calcular_resistencia_limitadora(v, vl, i)
    if r:
        print(f"{C_BOT} R Sugerida: {r:.2f}Ω")
        c, _ = m.buscar_resistencia_optima(r, p)
        if c: print(f"       ✅ {c['nombre']}")
    else:
        print(f"{C_SYS} Error voltaje.")


if __name__ == "__main__":
    main()