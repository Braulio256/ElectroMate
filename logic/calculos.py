import math

# --- LEY DE OHM ---
def calcular_corriente_ohm(v, r):
    return v / r if r != 0 else None

def calcular_voltaje_ohm(i, r):
    return i * r

def calcular_resistencia_ohm(v, i):
    return v / i if i != 0 else None

def calcular_potencia_dc(v, i):
    return v * i

def calcular_resistencia_limitadora(v_fuente, v_carga, i_objetivo):
    if v_fuente <= v_carga: return None, None
    v_r = v_fuente - v_carga
    r = v_r / i_objetivo
    p = v_r * i_objetivo
    return r, p

# --- FILTROS ---
def calcular_par_rc(motor, f, v):
    caps = [100e-12, 1e-9, 10e-9, 100e-9, 1e-6, 4.7e-6, 10e-6]
    mejor = None; min_err = 100
    for c_val in caps:
        cap, _ = motor.buscar_capacitor_optimo(c_val, v)
        if not cap: continue
        c_real = cap['parametros']['valor_faradios']
        r_nec = 1 / (2 * math.pi * f * c_real)
        res, _ = motor.buscar_resistencia_optima(r_nec, 0.125)
        if res:
            r_real = res['parametros']['valor_ohmios']
            f_real = 1 / (2 * math.pi * r_real * c_real)
            err = abs(1 - f_real/f)*100
            if err < min_err:
                min_err = err
                mejor = {"c": cap, "r": res, "f": f_real, "err": err}
    return mejor

def calcular_par_rl(motor, f, i_max):
    # Lógica simplificada para brevedad, expandir según necesidad
    ress = [10, 22, 47, 100, 220, 470, 1000]
    mejor = None; min_err = 100
    for r_val in ress:
        p_res = (i_max**2)*r_val
        res, _ = motor.buscar_resistencia_optima(r_val, p_res)
        if not res: continue
        r_real = res['parametros']['valor_ohmios']
        l_nec = r_real / (2*math.pi*f)
        ind, _ = motor.buscar_inductor_optimo(l_nec, i_max)
        if ind:
            l_real = ind['parametros']['valor_henrys']
            f_real = r_real / (2*math.pi*l_real)
            err = abs(1 - f_real/f)*100
            if err < min_err:
                min_err = err
                mejor = {"l": ind, "r": res, "f": f_real, "err": err}
    return mejor

def calcular_par_rlc(motor, f, v):
    caps = [100e-12, 1e-9, 10e-9, 100e-9, 1e-6]
    mejor = None; min_err = 100
    for c_val in caps:
        cap, _ = motor.buscar_capacitor_optimo(c_val, v)
        if not cap: continue
        c_real = cap['parametros']['valor_faradios']
        l_nec = 1 / (4 * (math.pi**2) * (f**2) * c_real)
        ind, _ = motor.buscar_inductor_optimo(l_nec, 0.1)
        if ind:
            l_real = ind['parametros']['valor_henrys']
            f_real = 1 / (2*math.pi*math.sqrt(l_real*c_real))
            err = abs(1 - f_real/f)*100
            if err < min_err:
                min_err = err
                mejor = {"l": ind, "c": cap, "f": f_real, "err": err}
    return mejor

def calcular_ganancia_opamp(motor, g):
    if g <= 1: return {"rf": None, "rg": None, "g": 1.0}
    rgs = [1000, 2200, 4700, 10000, 22000]
    mejor = None; min_err = 100
    for rg_val in rgs:
        rf_nec = rg_val * (g - 1)
        rf, _ = motor.buscar_resistencia_optima(rf_nec, 0.125)
        rg, _ = motor.buscar_resistencia_optima(rg_val, 0.125)
        if rf and rg:
            g_real = 1 + (rf['parametros']['valor_ohmios'] / rg['parametros']['valor_ohmios'])
            err = abs(1 - g_real/g)*100
            if err < min_err:
                min_err = err
                mejor = {"rf": rf, "rg": rg, "g": g_real}
    return mejor