import math
from logic.interfaz import input_profesional, C_BOT, C_SYS, CambioDeContexto
from logic.calculos import (
    calcular_par_rc, calcular_par_rl,
    calcular_par_rlc, calcular_ganancia_opamp
)


def resolver_filtro_ambiguo(datos, motor):
    print(f"{C_BOT} Solicitud ambigua. Seleccione tecnología:")
    print("       [1] Pasivo RC (Señal)")
    print("       [2] Activo (Op-Amps)")
    print("       [3] Inductivo RL (Potencia)")
    print("       [4] Resonante RLC (RF)")

    resp = input_profesional("Ingrese opción:", str).lower()

    if "2" in resp or "activo" in resp:
        raise CambioDeContexto("diseñar filtro activo")
    elif "4" in resp or "rlc" in resp:
        raise CambioDeContexto("diseñar filtro rlc")
    elif "3" in resp or "rl" in resp:
        raise CambioDeContexto("diseñar filtro rl")
    elif "1" in resp or "rc" in resp:
        print(f"{C_BOT} Seleccione respuesta RC:")
        print("       [1] Pasa Bajas (LP)")
        print("       [2] Pasa Altas (HP)")
        print("       [3] Rechaza Banda (Notch)")
        sub = input_profesional("Opción:", str).lower()
        if "1" in sub or "lp" in sub: raise CambioDeContexto("diseñar filtro pasa bajas")
        if "2" in sub or "hp" in sub: raise CambioDeContexto("diseñar filtro pasa altas")
        if "3" in sub or "notch" in sub: raise CambioDeContexto("diseñar filtro notch")
    else:
        print(f"{C_SYS} Opción no válida.")


def resolver_filtro_rc(datos, motor, tipo):
    nombres = {"LP": "Pasa Bajas", "HP": "Pasa Altas", "NOTCH": "Rechaza Banda"}
    print(f"{C_BOT} Diseño Filtro Pasivo RC - {nombres.get(tipo)}")

    f = datos.get('frecuencia')
    if f is None: f = input_profesional("Frecuencia de Corte (Hz):")
    v = datos.get('voltaje', 5.0)

    res = calcular_par_rc(motor, f, v)
    if res:
        print(f"{C_BOT} Resultados (F={res['f']:.1f}Hz):")
        print(f"       • R: {res['r']['nombre']}")
        print(f"       • C: {res['c']['nombre']}")
        if tipo == "LP":
            print("       (Config: R Serie -> C a Tierra)")
        elif tipo == "HP":
            print("       (Config: C Serie -> R a Tierra)")
        elif tipo == "NOTCH":
            print("       (Config: Red Twin-T)")
    else:
        print(f"{C_SYS} Sin resultados comerciales.")


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

    if tipo == "BP":
        fb = input_profesional("Frecuencia Baja (fL):")
        fa = input_profesional("Frecuencia Alta (fH):")
        v = input_profesional("Voltaje Op-Amp (V):")

        hp = calcular_par_rc(motor, fb, v)
        lp = calcular_par_rc(motor, fa, v, "bajo")
        opamp, _ = motor.buscar_opamp_apto(fa, v)

        if hp and lp and opamp:
            print(f"{C_BOT} Diseño BP Generado ({opamp['nombre']}):")
            print(f"       [HP] C={hp['c']['nombre']}, R={hp['r']['nombre']}")
            print(f"       [LP] R={lp['r']['nombre']}, C={lp['c']['nombre']}")
        return

    f = datos.get('frecuencia')
    if f is None: f = input_profesional("Frecuencia de Corte (Hz):")
    v = datos.get('voltaje')
    if v is None: v = input_profesional("Voltaje Op-Amp (V):")

    res = calcular_par_rc(motor, f, v)
    opamp, _ = motor.buscar_opamp_apto(f, v)

    if res and opamp:
        print(f"{C_BOT} Diseño {tipo} Generado ({opamp['nombre']}):")
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
    f = input_profesional("Frecuencia (Hz):")
    i = input_profesional("Corriente Máx (A):")
    res = calcular_par_rl(motor, f, i)
    if res:
        print(f"{C_BOT} L: {res['l']['nombre']} | R: {res['r']['nombre']}")
    else:
        print(f"{C_SYS} Sin inductores adecuados.")


def resolver_filtro_rlc(datos, motor):
    print(f"{C_BOT} Diseño Filtro RLC.")
    f = input_profesional("Frecuencia Resonancia (Hz):")
    res = calcular_par_rlc(motor, f, 5.0)
    if res:
        print(f"{C_BOT} L: {res['l']['nombre']} | C: {res['c']['nombre']}")
    else:
        print(f"{C_SYS} Sin componentes adecuados.")


def resolver_calc_fc_rc(datos):
    print(f"{C_BOT} Calculadora Frecuencia RC.")
    r = input_profesional("R (Ω):")
    c = input_profesional("C (uF):") / 1e6
    fc = 1 / (2 * math.pi * r * c)
    print(f"{C_BOT} Frecuencia: {fc:.2f} Hz")