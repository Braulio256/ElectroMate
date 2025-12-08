import math
from logic.interfaz import input_profesional, formatear_valor, C_BOT, C_SYS, CambioDeContexto
from logic.calculos import (
    calcular_par_rc, calcular_par_rl, calcular_par_rlc,
    calcular_ganancia_opamp, calcular_fc_rc_simple,
    calcular_fc_rl_simple, calcular_f0_rlc_simple
)


# --- MANEJO DE AMBIGÜEDAD DE DISEÑO ---
def resolver_filtro_ambiguo_total(datos, motor):
    print(f"{C_BOT} Solicitud de diseño ambigua. Necesito más detalles:")
    print("       [1] Pasivo RC (Resistencia/Capacitor - Audio/Señal)")
    print("       [2] Pasivo RL (Resistencia/Inductor - Potencia)")
    print("       [3] Activo (Op-Amps - Requiere Fuente)")
    print("       [4] Resonante RLC (Radiofrecuencia)")

    resp = input_profesional("Opción:", str).lower()

    if "3" in resp or "act" in resp:
        resolver_filtro_activo(datos, motor)
    elif "4" in resp or "rlc" in resp:
        resolver_filtro_rlc(datos, motor)
    elif "2" in resp or "rl" in resp:
        resolver_filtro_rl(datos, motor)
    elif "1" in resp or "rc" in resp:
        print(f"{C_BOT} ¿Tipo de respuesta RC?")
        print("       [1] Pasa Bajas (LP)")
        print("       [2] Pasa Altas (HP)")
        print("       [3] Rechaza Banda (Notch)")
        sub = input_profesional("Opción:", str).lower()
        if "1" in sub or "lp" in sub:
            resolver_filtro_rc(datos, motor, "LP")
        elif "2" in sub or "hp" in sub:
            resolver_filtro_rc(datos, motor, "HP")
        elif "3" in sub or "notch" in sub:
            resolver_filtro_rc(datos, motor, "NOTCH")
    else:
        print(f"{C_SYS} Opción no válida.")


def resolver_filtro_ambiguo_especifico(datos, motor, tipo_respuesta="LP"):
    print(f"{C_BOT} Quieres un filtro {tipo_respuesta}, pero ¿con qué tecnología?")
    print("       [1] Pasivo RC (Más simple)")
    print("       [2] Activo con Op-Amp (Mejor rendimiento/Ganancia)")

    op = input_profesional("Opción:", str).lower()
    if "2" in op or "act" in op:
        resolver_filtro_activo(datos, motor)  # Nota: El activo preguntará tipo de nuevo, pero es aceptable.
    else:
        resolver_filtro_rc(datos, motor, tipo_respuesta)


# --- MANEJO DE AMBIGÜEDAD DE CÁLCULO ---
def resolver_calculo_frecuencia_ambiguo(datos):
    print(f"{C_BOT} Quieres calcular frecuencia, pero necesito saber el circuito:")
    print("       [1] Circuito RC (Resistencia + Capacitor)")
    print("       [2] Circuito RL (Resistencia + Inductor)")
    print("       [3] Circuito LC/RLC (Resonancia)")

    op = input_profesional("Opción:", str).lower()

    if "1" in op or "rc" in op:
        resolver_calc_fc_rc(datos)
    elif "2" in op or "rl" in op:
        resolver_calc_fc_rl(datos)
    elif "3" in op or "lc" in op:
        resolver_calc_fc_rlc(datos)
    else:
        print(f"{C_SYS} No reconocí la opción.")


# --- CALCULADORAS ESPECÍFICAS (INVERSAS) ---
def resolver_calc_fc_rc(datos):
    print(f"{C_BOT} Calculadora Frecuencia de Corte RC.")
    r = datos.get('resistencia')
    c = datos.get('capacitancia')
    if not r: r = input_profesional("Valor R (Ω):")
    if not c: c = input_profesional("Valor C (F):")

    fc = calcular_fc_rc_simple(r, c)
    if fc:
        print(f"{C_BOT} Frecuencia de Corte: {formatear_valor(fc, 'Hz')}")
    else:
        print(f"{C_SYS} Error: Valores deben ser > 0")


def resolver_calc_fc_rl(datos):
    print(f"{C_BOT} Calculadora Frecuencia de Corte RL.")
    r = datos.get('resistencia')
    l = datos.get('inductancia')
    if not r: r = input_profesional("Valor R (Ω):")
    if not l: l = input_profesional("Valor L (H):")

    fc = calcular_fc_rl_simple(r, l)
    if fc:
        print(f"{C_BOT} Frecuencia de Corte: {formatear_valor(fc, 'Hz')}")
    else:
        print(f"{C_SYS} Error: Valores deben ser > 0")


def resolver_calc_fc_rlc(datos):
    print(f"{C_BOT} Calculadora Frecuencia de Resonancia LC.")
    l = datos.get('inductancia')
    c = datos.get('capacitancia')
    if not l: l = input_profesional("Valor L (H):")
    if not c: c = input_profesional("Valor C (F):")

    f0 = calcular_f0_rlc_simple(l, c)
    if f0:
        print(f"{C_BOT} Frecuencia Resonancia (Fo): {formatear_valor(f0, 'Hz')}")
    else:
        print(f"{C_SYS} Error: Valores deben ser > 0")


# --- DISEÑADORES (BUSCADORES DE COMPONENTES) ---
def resolver_filtro_rc(datos, motor, tipo):
    nombres = {"LP": "Pasa Bajas", "HP": "Pasa Altas", "NOTCH": "Rechaza Banda"}
    print(f"{C_BOT} Diseño Filtro Pasivo RC - {nombres.get(tipo, tipo)}")

    f = datos.get('frecuencia')
    if f is None: f = input_profesional("Frecuencia de Corte (Hz):")
    v = datos.get('voltaje', 5.0)

    res = calcular_par_rc(motor, f, v)
    if res:
        f_real_fmt = formatear_valor(res['f'], 'Hz')
        print(f"{C_BOT} Resultados (F={f_real_fmt}):")
        print(f"       • R: {res['r']['nombre']}")
        print(f"       • C: {res['c']['nombre']}")
        if tipo == "LP":
            print("       (Config: R Serie -> C a Tierra)")
        elif tipo == "HP":
            print("       (Config: C Serie -> R a Tierra)")
        elif tipo == "NOTCH":
            print("       (Config: Red Twin-T)")
    else:
        print(f"{C_SYS} Sin resultados comerciales exactos.")


def resolver_filtro_activo(datos, motor):
    print(f"{C_BOT} Diseño de Filtro ACTIVO (Op-Amp).")
    print("       [1] Pasa Bajas (LP) | [2] Pasa Altas (HP)")
    print("       [3] Pasa Banda (BP) | [4] Rechaza Banda (Notch)")

    resp = input_profesional("Opción:", str).lower()
    tipo = "LP"
    if "2" in resp or "hp" in resp:
        tipo = "HP"
    elif "3" in resp or "bp" in resp:
        tipo = "BP"
    elif "4" in resp or "notch" in resp:
        tipo = "NOTCH"

    # Lógica de Pasa Banda
    if tipo == "BP":
        fb = input_profesional("Frecuencia Baja (fL):")
        fa = input_profesional("Frecuencia Alta (fH):")
        v = input_profesional("Voltaje Op-Amp (V):")
        hp = calcular_par_rc(motor, fb, v)
        lp = calcular_par_rc(motor, fa, v)
        opamp, _ = motor.buscar_opamp_apto(fa, v)

        if hp and lp and opamp:
            print(f"{C_BOT} Diseño BP Generado ({opamp['nombre']}):")
            print(f"       [HP Etapa] C={hp['c']['nombre']}, R={hp['r']['nombre']}")
            print(f"       [LP Etapa] R={lp['r']['nombre']}, C={lp['c']['nombre']}")
        return

    # Lógica Estándar
    f = datos.get('frecuencia')
    if f is None: f = input_profesional("Frecuencia de Corte (Hz):")
    v = datos.get('voltaje')
    if v is None: v = input_profesional("Voltaje Op-Amp (V):")

    res = calcular_par_rc(motor, f, v)
    opamp, _ = motor.buscar_opamp_apto(f, v)

    if res and opamp:
        print(f"{C_BOT} Diseño {tipo} Activo ({opamp['nombre']}):")
        if tipo == "LP":
            print(f"       [RC] R={res['r']['nombre']}, C={res['c']['nombre']}")
        elif tipo == "HP":
            print(f"       [RC] C={res['c']['nombre']}, R={res['r']['nombre']}")
        elif tipo == "NOTCH":
            print(f"       [Twin-T] R={res['r']['nombre']}, C={res['c']['nombre']}")
    else:
        print(f"{C_SYS} No hay componentes adecuados.")


def resolver_filtro_rl(datos, motor):
    print(f"{C_BOT} Diseño Filtro RL (Inductivo).")
    f = datos.get('frecuencia')
    if not f: f = input_profesional("Frecuencia (Hz):")
    i = input_profesional("Corriente Máx (A):")

    res = calcular_par_rl(motor, f, i)
    if res:
        f_fmt = formatear_valor(res['f'], 'Hz')
        print(f"{C_BOT} Solución RL (F={f_fmt}):")
        print(f"       • L: {res['l']['nombre']}")
        print(f"       • R: {res['r']['nombre']}")
    else:
        print(f"{C_SYS} Sin inductores adecuados.")


def resolver_filtro_rlc(datos, motor):
    print(f"{C_BOT} Diseño Filtro RLC (Resonante).")
    f = datos.get('frecuencia')
    if not f: f = input_profesional("Frecuencia Resonancia (Hz):")
    res = calcular_par_rlc(motor, f, 5.0)
    if res:
        f_fmt = formatear_valor(res['f'], 'Hz')
        print(f"{C_BOT} Tanque LC (Fo={f_fmt}):")
        print(f"       • L: {res['l']['nombre']}")
        print(f"       • C: {res['c']['nombre']}")
    else:
        print(f"{C_SYS} Sin componentes adecuados.")