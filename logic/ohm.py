from logic.interfaz import input_profesional, C_BOT, C_SYS
from logic.calculos import (
    calcular_voltaje_ohm, calcular_potencia_dc,
    calcular_corriente_ohm, calcular_resistencia_ohm,
    calcular_resistencia_limitadora
)


def resolver_voltaje(datos, motor):
    print(f"{C_BOT} Cálculo V = I * R")
    i = datos.get('corriente')
    r = datos.get('resistencia')

    if not i: i = input_profesional("Corriente (mA):") / 1000.0
    if not r: r = input_profesional("Resistencia (Ω):")

    v = calcular_voltaje_ohm(i, r)
    p = calcular_potencia_dc(v, i)

    print(f"{C_BOT} V: {v:.2f}V | P: {p:.3f}W")
    c, _ = motor.buscar_resistencia_optima(r, p)
    if c: print(f"       ✅ {c['nombre']}")


def resolver_corriente(datos, motor):
    print(f"{C_BOT} Cálculo I = V / R")
    v = datos.get('voltaje')
    r = datos.get('resistencia')

    if not v: v = input_profesional("Voltaje (V):")
    if not r: r = input_profesional("Resistencia (Ω):")

    if r <= 0: print(f"{C_SYS} Error: Resistencia debe ser mayor a 0."); return

    i = calcular_corriente_ohm(v, r)
    p = calcular_potencia_dc(v, i)

    print(f"{C_BOT} I: {i * 1000:.1f}mA | P: {p:.3f}W")
    c, _ = motor.buscar_resistencia_optima(r, p)
    if c:
        print(f"       ✅ {c['nombre']} aguanta.")
    else:
        print("       ⚠️ Resistencia pequeña se quema.")


def resolver_resistencia(datos, motor):
    print(f"{C_BOT} Cálculo R = V / I")
    v = datos.get('voltaje')
    i = datos.get('corriente')

    if not v: v = input_profesional("Voltaje (V):")
    if not i: i = input_profesional("Corriente (mA):") / 1000.0

    if i <= 0: print(f"{C_SYS} Error: Corriente debe ser mayor a 0."); return

    r = calcular_resistencia_ohm(v, i)
    p = calcular_potencia_dc(v, i)

    print(f"{C_BOT} R: {r:.2f}Ω")
    c, _ = motor.buscar_resistencia_optima(r, p)
    if c: print(f"       ✅ Usa: {c['nombre']}")


def resolver_potencia(datos, motor):
    print(f"{C_BOT} Cálculo P = V * I")
    v = datos.get('voltaje')
    i = datos.get('corriente')

    if not v: v = input_profesional("Voltaje (V):")
    if not i: i = input_profesional("Corriente (mA):") / 1000.0

    p = calcular_potencia_dc(v, i)
    print(f"{C_BOT} Potencia: {p:.4f}W")


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
        print(f"{C_BOT} R Sugerida: {r:.2f}Ω")
        c, _ = motor.buscar_resistencia_optima(r, p)
        if c: print(f"       ✅ {c['nombre']}")
    else:
        print(f"{C_SYS} Error: Voltaje insuficiente.")