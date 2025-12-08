from logic.interfaz import input_profesional, parsear_valor, formatear_valor, C_BOT, C_SYS
from logic.calculos import (
    calcular_voltaje_ohm, calcular_potencia_dc,
    calcular_corriente_ohm, calcular_resistencia_ohm,
    calcular_resistencia_limitadora, calcular_divisor_voltaje,
    calcular_bateria_duracion, calcular_equivalente_resistencias,
    calcular_equivalente_capacitores, calcular_tau_rc,
    calcular_tau_rl
)


def input_lista_valores(mensaje):
    """Lee lista y muestra feedback de lo detectado."""
    raw = input_profesional(mensaje, str)
    raw = raw.replace(",", " ").replace(" y ", " ")
    partes = raw.split()
    valores = []
    textos_detectados = []

    for p in partes:
        val = parsear_valor(p)
        if val is not None:
            valores.append(val)
            textos_detectados.append(formatear_valor(val))
        else:
            print(f"{C_SYS} Ignorando texto no numérico: '{p}'")

    if valores:
        print(f"{C_SYS} Valores detectados: {', '.join(textos_detectados)}")
    return valores


def resolver_reduccion_resistencias(datos, motor):
    print(f"{C_BOT} Cálculo de Resistencia Equivalente (Req).")
    print("       ¿Configuración?")
    print("       [1] Serie (Suma)")
    print("       [2] Paralelo (Inversa)")

    op = input_profesional("Opción:", str).lower()
    tipo = "serie"
    if "2" in op or "para" in op or "//" in op:
        tipo = "paralelo"

    print(f"{C_BOT} Modo: {tipo.upper()}")

    vals = input_lista_valores("Ingrese resistencias (ej: 1M 470 1.2k):")

    if len(vals) < 2:
        print(f"{C_SYS} Necesito al menos 2 valores.")
        return

    req = calcular_equivalente_resistencias(vals, tipo)
    print(f"{C_BOT} Req Total: {formatear_valor(req, 'Ω')}")


def resolver_reduccion_capacitores(datos, motor):
    print(f"{C_BOT} Cálculo de Capacitancia Equivalente (Ceq).")
    print("       [1] Serie (1/Ceq...)")
    print("       [2] Paralelo (Suma)")

    op = input_profesional("Opción:", str).lower()
    tipo = "serie"
    if "2" in op or "para" in op:
        tipo = "paralelo"

    print(f"{C_BOT} Modo: {tipo.upper()}")
    vals = input_lista_valores("Ingrese capacitores (ej: 10u 100n):")

    if not vals: return

    ceq = calcular_equivalente_capacitores(vals, tipo)
    print(f"{C_BOT} Ceq Total: {formatear_valor(ceq, 'F')}")


def resolver_transitorio_tau(datos, motor):
    print(f"{C_BOT} Análisis Transitorio (Tau).")
    print("       [1] Circuito RC")
    print("       [2] Circuito RL")

    op = input_profesional("Tipo:", str).lower()
    tau = 0

    if "1" in op or "rc" in op:
        r = input_profesional("Resistencia (Ω):")
        c = input_profesional("Capacitor (uF/nF):")
        tau = calcular_tau_rc(r, c)
        print(f"{C_BOT} Constante (τ): {formatear_valor(tau, 's')}")

    elif "2" in op or "rl" in op:
        r = input_profesional("Resistencia (Ω):")
        l = input_profesional("Inductor (mH):")
        tau = calcular_tau_rl(r, l)
        print(f"{C_BOT} Constante (τ): {formatear_valor(tau, 's')}")

    if tau > 0:
        print("-" * 40)
        print(f"       • 5τ (Carga completa): {formatear_valor(tau * 5, 's')}")
        print("-" * 40)


# --- RESOLVEDORES LEY DE OHM (Sin cambios en lógica, solo imports) ---

def resolver_voltaje(datos, motor):
    print(f"{C_BOT} Cálculo V = I * R")
    i = datos.get('corriente');
    r = datos.get('resistencia')
    if not i: i = input_profesional("Corriente (mA):") / 1000.0
    if not r: r = input_profesional("Resistencia (Ω):")
    v = calcular_voltaje_ohm(i, r);
    p = calcular_potencia_dc(v, i)
    print(f"{C_BOT} V: {formatear_valor(v, 'V')} | P: {formatear_valor(p, 'W')}")
    c, _ = motor.buscar_resistencia_optima(r, p)
    if c: print(f"       ✅ {c['nombre']}")


def resolver_corriente(datos, motor):
    print(f"{C_BOT} Cálculo I = V / R")
    v = datos.get('voltaje');
    r = datos.get('resistencia')
    if not v: v = input_profesional("Voltaje (V):")
    if not r: r = input_profesional("Resistencia (Ω):")
    if r <= 0: print(f"{C_SYS} Error: R > 0"); return
    i = calcular_corriente_ohm(v, r);
    p = calcular_potencia_dc(v=v, i=i)
    print(f"{C_BOT} I: {formatear_valor(i, 'A')} | P: {formatear_valor(p, 'W')}")
    c, _ = motor.buscar_resistencia_optima(r, p)
    if c: print(f"       ✅ {c['nombre']}")


def resolver_resistencia(datos, motor):
    print(f"{C_BOT} Cálculo R = V / I")
    v = datos.get('voltaje');
    i = datos.get('corriente')
    if not v: v = input_profesional("Voltaje (V):")
    if not i: i = input_profesional("Corriente (mA):") / 1000.0
    if i <= 0: print(f"{C_SYS} Error: I > 0"); return
    r = calcular_resistencia_ohm(v, i);
    p = calcular_potencia_dc(v=v, i=i)
    print(f"{C_BOT} R: {formatear_valor(r, 'Ω')}")
    c, _ = motor.buscar_resistencia_optima(r, p)
    if c: print(f"       ✅ Usa: {c['nombre']}")


def resolver_potencia(datos, motor):
    print(f"{C_BOT} Cálculo P = V * I")
    v = datos.get('voltaje');
    i = datos.get('corriente')
    if not v: v = input_profesional("Voltaje (V):")
    if not i: i = input_profesional("Corriente (mA):") / 1000.0
    p = calcular_potencia_dc(v, i)
    print(f"{C_BOT} Potencia: {formatear_valor(p, 'W')}")


def resolver_led(datos, motor):
    print(f"{C_BOT} Cálculo R Limitadora LED")
    v = datos.get('voltaje')
    if not v: v = input_profesional("V Fuente:")
    try:
        vl = input_profesional("V Carga/LED:")
    except:
        return
    i = datos.get('corriente')
    if not i: i = input_profesional("I Carga (mA):") / 1000.0
    r, p = calcular_resistencia_limitadora(v, vl, i)
    if r:
        print(f"{C_BOT} R Sugerida: {formatear_valor(r, 'Ω')}")
        c, _ = motor.buscar_resistencia_optima(r, p)
        if c: print(f"       ✅ Usa: {c['nombre']}")
    else:
        print(f"{C_SYS} Error voltaje.")


def resolver_divisor_voltaje(datos, motor):
    print(f"{C_BOT} Cálculo Divisor de Voltaje")
    vin = datos.get('voltaje')
    if not vin: vin = input_profesional("Vin:")
    r1 = input_profesional("R1 (Superior):")
    r2 = input_profesional("R2 (Inferior):")
    vout = calcular_divisor_voltaje(vin, r1, r2)
    if vout is not None: print(f"{C_BOT} Vout: {formatear_valor(vout, 'V')}")


def resolver_energia(datos, motor):
    print(f"{C_BOT} Cálculo Energía")
    op = input_profesional("1. Wh Consumidos | 2. Duración Batería", str)
    if "1" in op:
        p = input_profesional("Watts:")
        t = input_profesional("Horas:")
        print(f"{C_BOT} {p * t:.2f} Wh")
    elif "2" in op:
        cap = input_profesional("Batería (mAh):") / 1000.0
        cons = input_profesional("Consumo (mA):") / 1000.0
        h = calcular_bateria_duracion(cap, cons)
        print(f"{C_BOT} Duración: {h:.2f} Horas")