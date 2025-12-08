import math


# --- LEY DE OHM Y POTENCIA  ---

def calcular_corriente_ohm(voltaje, resistencia):
    """Retorna Amperios (I = V / R)"""
    if resistencia <= 0: return None
    return voltaje / resistencia


def calcular_voltaje_ohm(corriente, resistencia):
    """Retorna Voltios (V = I * R)"""
    return corriente * resistencia


def calcular_resistencia_ohm(voltaje, corriente):
    """Retorna Ohms (R = V / I)"""
    if corriente <= 0: return None
    return voltaje / corriente


def calcular_potencia_dc(voltaje, corriente):
    """Retorna Watts (P = V * I)"""
    return voltaje * corriente


def calcular_resistencia_limitadora(v_fuente, v_carga, i_objetivo):
    """
    Calcula R serie para limitar corriente a cualquier CARGA.
    (LEDs, Zeners, Bases de transistor, etc.)
    Retorna (Resistencia_Ohms, Potencia_Disipada_Watts)
    """
    if v_fuente <= v_carga: return None, None

    # El voltaje que debe absorber la resistencia
    v_caida_resistencia = v_fuente - v_carga

    r_necesaria = calcular_resistencia_ohm(v_caida_resistencia, i_objetivo)
    p_disipada = calcular_potencia_dc(v_caida_resistencia, i_objetivo)

    return r_necesaria, p_disipada


# --- FILTROS  ---

def calcular_par_rc(motor, frecuencia, voltaje, tipo_capacitor="general"):
    capacitores_prueba = []

    print(f"\n[PARAMETRO C] Para {frecuencia} Hz:")
    entrada = input("Valor Capacitor (uF) o ENTER para auto: ")
    if entrada.strip():
        try:
            capacitores_prueba = [float(entrada) / 1e6]
        except:
            pass

    if not capacitores_prueba:
        if tipo_capacitor == "bajo":
            capacitores_prueba = [100e-12, 22e-12, 10e-9, 1e-9]
        else:
            capacitores_prueba = [100e-9, 10e-9, 1e-6, 4.7e-6, 470e-9, 22e-6, 100e-6]

    mejor_combinacion = None
    menor_error = 100.0

    for valor_c_prueba in capacitores_prueba:
        cap_real, msg = motor.buscar_capacitor_optimo(valor_c_prueba, voltaje)

        if not cap_real and entrada.strip():
            cap_real = {"nombre": f"Generico {entrada}uF", "parametros": {"valor_faradios": valor_c_prueba}}
        elif not cap_real:
            continue

        val_c = cap_real['parametros']['valor_faradios']
        res_necesaria = 1 / (2 * math.pi * frecuencia * val_c)
        res_real, msg_r = motor.buscar_resistencia_optima(res_necesaria, 0.125)

        if res_real:
            val_r = res_real['parametros']['valor_ohmios']
            f_real = 1 / (2 * math.pi * val_r * val_c)
            error = abs(1 - (f_real / frecuencia)) * 100
            if error < menor_error:
                menor_error = error
                mejor_combinacion = {"c": cap_real, "r": res_real, "f": f_real, "err": error}
    return mejor_combinacion


def calcular_par_rl(motor, frecuencia, corriente_max):
    print(f"\n[PARAMETRO L] Para {frecuencia} Hz:")
    entrada = input("Valor Inductor (mH) o ENTER para auto: ")
    l_manual = None
    if entrada.strip():
        try:
            l_manual = float(entrada) / 1000.0
        except:
            pass

    if l_manual:
        r_nec = frecuencia * 2 * math.pi * l_manual
        res_real, _ = motor.buscar_resistencia_optima(r_nec, corriente_max ** 2 * r_nec)
        if res_real:
            f_real = res_real['parametros']['valor_ohmios'] / (2 * math.pi * l_manual)
            err = abs(1 - (f_real / frecuencia)) * 100
            return {"l": {"nombre": f"Generico {entrada}mH"}, "r": res_real, "f": f_real, "err": err}
        return None

    if corriente_max > 0.5:
        resistencias = [10, 22, 47, 100]
    else:
        resistencias = [1000, 2200, 4700, 10000]

    mejor_combinacion = None
    menor_error = 100.0

    for val_r in resistencias:
        potencia = (corriente_max ** 2) * val_r
        res_real, _ = motor.buscar_resistencia_optima(val_r, potencia)
        if not res_real: continue

        r_ohm = res_real['parametros']['valor_ohmios']
        l_nec = r_ohm / (2 * math.pi * frecuencia)
        ind_real, _ = motor.buscar_inductor_optimo(l_nec, corriente_max)

        if ind_real:
            val_l = ind_real['parametros']['valor_henrys']
            f_real = r_ohm / (2 * math.pi * val_l)
            error = abs(1 - (f_real / frecuencia)) * 100
            if error < menor_error:
                menor_error = error
                mejor_combinacion = {"l": ind_real, "r": res_real, "f": f_real, "err": error}
    return mejor_combinacion


def calcular_par_rlc(motor, frecuencia, voltaje):
    capacitores_prueba = [100e-12, 1e-9, 10e-9, 100e-9, 1e-6]
    mejor_combinacion = None
    menor_error = 100.0

    print("... Iterando combinaciones LC resonantes ...")

    for val_c_test in capacitores_prueba:
        cap_real, _ = motor.buscar_capacitor_optimo(val_c_test, voltaje)
        if not cap_real: continue

        val_c = cap_real['parametros']['valor_faradios']
        l_necesaria = 1 / (4 * (math.pi ** 2) * (frecuencia ** 2) * val_c)
        ind_real, _ = motor.buscar_inductor_optimo(l_necesaria, 0.1)

        if ind_real:
            val_l = ind_real['parametros']['valor_henrys']
            f_real = 1 / (2 * math.pi * math.sqrt(val_l * val_c))
            error = abs(1 - (f_real / frecuencia)) * 100

            if error < menor_error:
                menor_error = error
                mejor_combinacion = {"l": ind_real, "c": cap_real, "f": f_real, "err": error}
    return mejor_combinacion


def calcular_ganancia_opamp(motor, ganancia_deseada):
    if ganancia_deseada <= 1: return {"rf": None, "rg": None, "tipo": "Buffer", "g_real": 1.0}

    r_g_candidatas = [1000, 2200, 4700, 10000, 22000]
    mejor_config = None
    menor_error_g = 100.0

    for rg_val in r_g_candidatas:
        rf_necesaria = rg_val * (ganancia_deseada - 1)
        rf_real, _ = motor.buscar_resistencia_optima(rf_necesaria, 0.125)

        if rf_real:
            rf_val = rf_real['parametros']['valor_ohmios']
            g_real = 1 + (rf_val / rg_val)
            error = abs(1 - (g_real / ganancia_deseada)) * 100

            if error < menor_error_g:
                menor_error_g = error
                rg_real, _ = motor.buscar_resistencia_optima(rg_val, 0.125)
                mejor_config = {"rf": rf_real, "rg": rg_real, "g_real": g_real, "tipo": "Amp No-Inversor"}
    return mejor_config