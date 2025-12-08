import math

# --- LEY DE OHM (YA EXISTENTE) ---
def calcular_corriente_ohm(v, r): return v / r if r != 0 else None
def calcular_voltaje_ohm(i, r): return i * r
def calcular_resistencia_ohm(v, i): return v / i if i != 0 else None
def calcular_conductancia(r): return 1 / r if r != 0 else None

# --- POTENCIA Y ENERGIA (YA EXISTENTE) ---
def calcular_potencia_dc(v=None, i=None, r=None):
    if v is not None and i is not None: return v * i
    if i is not None and r is not None: return (i**2) * r
    if v is not None and r is not None and r != 0: return (v**2) / r
    return None

def calcular_energia_joules(p, t): return p * t
def calcular_bateria_duracion(cap_ah, i): return cap_ah / i if i > 0 else None

# --- APLICACIONES DE OHM (YA EXISTENTE) ---
def calcular_resistencia_limitadora(vf, vc, i):
    if vf <= vc: return None, None
    vr = vf - vc
    return vr/i, vr*i

def calcular_divisor_voltaje(vin, r1, r2):
    if (r1+r2) == 0: return None
    return vin * (r2 / (r1+r2))

# --- NUEVO: REDUCCION DE CIRCUITOS (SERIE/PARALELO) ---
def calcular_equivalente_resistencias(lista_valores, tipo="serie"):
    """Calcula Req para Resistencias o Inductores"""
    if not lista_valores: return 0
    if tipo == "serie":
        return sum(lista_valores)
    elif tipo == "paralelo":
        if 0 in lista_valores: return 0 # Cortocircuito
        suma_inversa = sum(1/r for r in lista_valores)
        return 1 / suma_inversa

def calcular_equivalente_capacitores(lista_valores, tipo="serie"):
    """Calcula Ceq (La lógica es inversa a las resistencias)"""
    if not lista_valores: return 0
    if tipo == "paralelo":
        return sum(lista_valores)
    elif tipo == "serie":
        if 0 in lista_valores: return 0
        suma_inversa = sum(1/c for c in lista_valores)
        return 1 / suma_inversa

# --- NUEVO: ANALISIS TRANSITORIO (TAU) ---
def calcular_tau_rc(r, c):
    """Constante de tiempo para circuito RC"""
    return r * c

def calcular_tau_rl(r, l):
    """Constante de tiempo para circuito RL"""
    return l / r if r != 0 else 0

def estado_carga_transitorio(tau, tiempo):
    """Devuelve el % de carga según el tiempo transcurrido"""
    if tau == 0: return 100.0
    # Formula de carga: 1 - e^(-t/tau)
    porcentaje = (1 - math.exp(-tiempo / tau)) * 100
    return porcentaje

# --- FILTROS (Se mantienen igual, solo mostramos el import) ---
def calcular_par_rc(motor, f, v):
    # (Mantener el código anterior de filtros RC)
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
    # (Mantener código anterior RL)
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
    # (Mantener código anterior RLC)
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
    # (Mantener código anterior OPAMP)
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