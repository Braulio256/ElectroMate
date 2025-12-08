import math
from logic.buscador import BuscadorComponentes


def sistema_experto():
    print("=== SISTEMA EXPERTO DE DISENO ELECTRONICO v2.2 (Filtros Activos Completos) ===")
    motor = BuscadorComponentes()

    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1. Calcular Resistencia (Ley de Ohm)")
        print("2. Disenar Filtros (Suite Completa)")
        print("0. Salir")

        opcion = input("Seleccione una opcion: ")

        if opcion == "1":
            modo_resistencia(motor)
        elif opcion == "2":
            menu_filtros_principal(motor)
        elif opcion == "0":
            print("Cerrando sistema...")
            break
        else:
            print("[ERROR] Opcion no valida.")


def modo_resistencia(motor):
    print("\n[MODO] CALCULO DE RESISTENCIA")
    try:
        voltaje_fuente = float(input("Ingrese Voltaje de la Fuente (V): "))
        voltaje_carga = float(input("Ingrese Voltaje del componente (V): "))
        corriente_mA = float(input("Ingrese Corriente deseada (mA): "))

        corriente_A = corriente_mA / 1000.0
        voltaje_resistencia = voltaje_fuente - voltaje_carga

        if voltaje_resistencia <= 0:
            print("[ERROR] La fuente debe ser mayor al voltaje del componente.")
            return

        resistencia_teorica = voltaje_resistencia / corriente_A
        potencia_teorica = voltaje_resistencia * corriente_A

        print(f"\n[CALCULO TEORICO]")
        print(f"Resistencia: {resistencia_teorica:.2f} Ohms")
        print(f"Potencia:    {potencia_teorica:.4f} Watts")

        componente, mensaje = motor.buscar_resistencia_optima(resistencia_teorica, potencia_teorica)

        print(f"\n[RESULTADO DEL SISTEMA]")
        if componente:
            print(f"Componente: {componente['nombre']}")
            print(f"ID:         {componente['id']}")
        else:
            print(f"[FALLO] {mensaje}")

    except ValueError:
        print("[ERROR] Solo numeros.")


# --- FUNCIONES DE CALCULO ---
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
    """
    Calcula resistencias para Amplificador No Inversor.
    Formula: G = 1 + (Rf / Rg)
    """
    if ganancia_deseada <= 1:
        return {"rf": None, "rg": None, "tipo": "Buffer (Seguidor de Voltaje)"}

    # Fijamos Rg (Resistencia a tierra) en valores comunes
    r_g_candidatas = [1000, 2200, 4700, 10000, 22000, 47000, 100000]
    mejor_config = None
    menor_error_g = 100.0

    for rg_val in r_g_candidatas:
        # Calculamos Rf necesaria: Rf = Rg * (G - 1)
        rf_necesaria = rg_val * (ganancia_deseada - 1)

        # Buscamos Rf comercial
        rf_real, _ = motor.buscar_resistencia_optima(rf_necesaria, 0.125)

        if rf_real:
            rf_val = rf_real['parametros']['valor_ohmios']
            g_real = 1 + (rf_val / rg_val)
            error = abs(1 - (g_real / ganancia_deseada)) * 100

            if error < menor_error_g:
                menor_error_g = error
                # Buscamos el objeto Rg tambien para mostrar nombre comercial
                rg_real, _ = motor.buscar_resistencia_optima(rg_val, 0.125)
                mejor_config = {
                    "rf": rf_real,
                    "rg": rg_real,
                    "g_real": g_real,
                    "tipo": "Amplificador No-Inversor"
                }

    return mejor_config


# --- MENUS ---
def menu_filtros_principal(motor):
    print("\n--- CATEGORIA DE FILTROS ---")
    print("1. Filtros Pasivos RC")
    print("2. Filtros Pasivos RL")
    print("3. Filtros Pasivos RLC")
    print("4. Filtros Activos (Op-Amps + RC)")
    print("0. Volver")

    cat = input("Seleccione categoria: ")

    if cat == "1":
        menu_filtros_rc(motor)
    elif cat == "2":
        menu_filtros_rl(motor)
    elif cat == "3":
        menu_filtros_rlc(motor)
    elif cat == "4":
        menu_filtros_activos(motor)
    elif cat == "0":
        return


def menu_filtros_rc(motor):
    print("\n--- FILTROS PASIVOS RC ---")
    print("1. Pasa Bajas")
    print("2. Pasa Altas")
    print("3. Rechaza Banda (Twin-T)")
    print("4. Pasa Banda (Pasivo)")
    print("5. CALC: Freq = 1/(2*pi*R*C)")

    tipo = input("Seleccione: ")
    if tipo not in ["1", "2", "3", "4", "5"]: return

    try:
        if tipo == "5":
            r = float(input("R (Ohms): "))
            c = float(input("C (uF): "))
            print(f"✅ Freq: {1 / (2 * math.pi * r * (c / 1e6)):.2f} Hz")
            return

        v = float(input("Voltaje (V): "))
        if tipo == "4":
            print("[PASA BANDA RC]")
            fb = float(input("Freq Baja: "))
            fa = float(input("Freq Alta: "))
            hp = calcular_par_rc(motor, fb, v)
            lp = calcular_par_rc(motor, fa, v, "bajo")
            if hp and lp:
                print(f"HP: C={hp['c']['nombre']}, R={hp['r']['nombre']}")
                print(f"LP: R={lp['r']['nombre']}, C={lp['c']['nombre']}")
            return

        f = float(input("Frecuencia (Hz): "))
        res = calcular_par_rc(motor, f, v)
        if not res: print("[FALLO]"); return

        print(f"\n[RC CALCULADO] Freq: {res['f']:.1f}Hz")
        if tipo == "1":
            print(f"LP: R={res['r']['nombre']} -> C={res['c']['nombre']}")
        elif tipo == "2":
            print(f"HP: C={res['c']['nombre']} -> R={res['r']['nombre']}")
        elif tipo == "3":
            print("Twin-T: Ver esquema complejo.")

    except ValueError:
        print("[ERROR] Invalido.")


def menu_filtros_rl(motor):
    print("\n--- FILTROS PASIVOS RL ---")
    print("1. Pasa Bajas RL")
    print("2. Pasa Altas RL")
    print("3. Pasa Banda RL")
    print("4. CALC: Freq = R/(2*pi*L)")

    tipo = input("Seleccione: ")
    if tipo not in ["1", "2", "3", "4"]: return

    try:
        if tipo == "4":
            r = float(input("R (Ohms): "))
            l = float(input("L (mH): "))
            print(f"✅ Freq: {r / (2 * math.pi * (l / 1000)):.2f} Hz")
            return

        i = float(input("Corriente (A): "))
        if tipo == "3":
            print("[PASA BANDA RL]")
            fb = float(input("Freq Baja: "))
            fa = float(input("Freq Alta: "))
            hp = calcular_par_rl(motor, fb, i)
            lp = calcular_par_rl(motor, fa, i)
            if hp and lp:
                print(f"HP: R={hp['r']['nombre']}, L={hp['l']['nombre']}")
                print(f"LP: L={lp['l']['nombre']}, R={lp['r']['nombre']}")
            return

        f = float(input("Frecuencia (Hz): "))
        res = calcular_par_rl(motor, f, i)
        if res:
            print(f"\n[RL CALCULADO] Freq: {res['f']:.1f}Hz")
            if tipo == "1":
                print(f"LP: L={res['l']['nombre']} -> R={res['r']['nombre']}")
            else:
                print(f"HP: R={res['r']['nombre']} -> L={res['l']['nombre']}")
        else:
            print("[FALLO]")
    except ValueError:
        print("[ERROR] Invalido.")


def menu_filtros_rlc(motor):
    print("\n--- FILTROS PASIVOS RLC ---")
    print("1. Pasa Banda")
    print("2. Rechaza Banda")
    print("3. CALC: Freq = 1/(2*pi*sqrt(LC))")

    tipo = input("Seleccione: ")
    if tipo not in ["1", "2", "3"]: return

    try:
        if tipo == "3":
            print("\n[CALCULADORA RESONANCIA]")
            l_mH = float(input("Inductor (mH): "))
            c_uF = float(input("Capacitor (uF): "))
            l = l_mH / 1000.0;
            c = c_uF / 1e6
            freq = 1 / (2 * math.pi * math.sqrt(l * c))
            print(f"✅ Frecuencia Resonancia: {freq:.2f} Hz")
            return

        f = float(input("Frecuencia Central (Hz): "))
        v = float(input("Voltaje (V): "))
        res = calcular_par_rlc(motor, f, v)

        if res:
            print(f"\n[RLC CALCULADO] Freq Central: {res['f']:.1f}Hz")
            print(f"Componentes LC: {res['l']['nombre']} + {res['c']['nombre']}")

            # Calculo R comercial para Q=10
            xl = 2 * math.pi * f * res['l']['parametros']['valor_henrys']
            r_ideal = xl / 10.0
            r_com, _ = motor.buscar_resistencia_optima(r_ideal, 0.25)

            print(f"Ajuste Q=10: Resistencia sugerida ~{r_ideal:.1f}Ω")
            if r_com: print(f"--> Comercial: {r_com['nombre']}")

            if tipo == "1":
                print("Pasa Banda: R Serie -> [L+C Serie] -> Salida")
            elif tipo == "2":
                print("Rechaza Banda: R Serie -> Salida (con [L+C] a tierra)")
        else:
            print("[FALLO]")
    except ValueError:
        print("[ERROR] Invalido.")


def menu_filtros_activos(motor):
    print("\n--- FILTROS ACTIVOS (OP-AMP) ---")
    print("1. Pasa Bajas (Active LP)")
    print("2. Pasa Altas (Active HP)")
    print("3. Pasa Banda (Active BP - Cascada)")
    print("4. Rechaza Banda (Active Notch - Buffered Twin-T)")

    tipo = input("Seleccione: ")
    if tipo not in ["1", "2", "3", "4"]: return

    try:
        v = float(input("Voltaje Op-Amp (V): "))

        # --- PREGUNTA POR GANANCIA (COMUN A TODOS) ---
        ganancia = 1.0
        entrada_g = input("Ganancia deseada (Ej: 1, 2, 10) [Enter=1]: ")
        if entrada_g.strip(): ganancia = float(entrada_g)

        # Calculamos resistencias de ganancia
        conf_ganancia = calcular_ganancia_opamp(motor, ganancia)

        # --- OPCION 3: PASA BANDA ---
        if tipo == "3":
            fb = float(input("Fq Baja (Corte inferior): "))
            fa = float(input("Fq Alta (Corte superior): "))
            hp = calcular_par_rc(motor, fb, v)
            lp = calcular_par_rc(motor, fa, v, "bajo")
            op, _ = motor.buscar_opamp_apto(fa, v)

            if hp and lp and op:
                print(f"\n✅ [PASA BANDA ACTIVO] Chip: {op['nombre']}")
                print(f"Etapa 1 (HP): C={hp['c']['nombre']}, R={hp['r']['nombre']}")
                print(f"Etapa 2 (LP): R={lp['r']['nombre']}, C={lp['c']['nombre']}")

                print(f"--- Amplificacion ({conf_ganancia['tipo']}) ---")
                if conf_ganancia['rf']:
                    print(f"Resistencia Feedback (Rf): {conf_ganancia['rf']['nombre']}")
                    print(f"Resistencia a Gnd (Rg):    {conf_ganancia['rg']['nombre']}")
                    print(f"Ganancia Real: x{conf_ganancia['g_real']:.2f}")
                else:
                    print("Configuracion: Buffer (Salida directa a entrada inverdora -)")
            return

        # --- OPCION 4: RECHAZA BANDA (ACTIVE NOTCH) ---
        if tipo == "4":
            f = float(input("Frecuencia a ELIMINAR (Notch): "))
            res = calcular_par_rc(motor, f, v)
            op, _ = motor.buscar_opamp_apto(f, v)

            if res and op:
                print(f"\n✅ [ACTIVE NOTCH / TWIN-T] Chip: {op['nombre']}")
                r_nom = res['r']['nombre']
                c_nom = res['c']['nombre']
                print("Este filtro requiere precisión. Usa componentes al 1%.")
                print("--- Rama Superior (Pasa Bajas T) ---")
                print(f"   2x Resistencias en Serie: {r_nom}")
                print(f"   1x Capacitor a Gnd (2C):  Poner 2 unidades de {c_nom} en PARALELO")
                print("--- Rama Inferior (Pasa Altas T) ---")
                print(f"   2x Capacitores en Serie:  {c_nom}")
                print(f"   1x Resistencia a Gnd (R/2): Poner 2 unidades de {r_nom} en PARALELO")
                print("--- Buffer ---")
                print("Salida del filtro a Entrada (+) del OpAmp. Configurado como Buffer (G=1).")
            return

        # --- OPCIONES 1 y 2 (LP / HP STANDARD) ---
        f = float(input("Frecuencia (Hz): "))
        res = calcular_par_rc(motor, f, v)
        op, _ = motor.buscar_opamp_apto(f, v)

        if res and op:
            print(f"\n✅ [FILTRO ACTIVO CALCULADO] Chip: {op['nombre']}")
            if tipo == "1":
                print(f"Topologia: Pasa Bajas (Entrada +)")
                print(f"Componentes RC: R={res['r']['nombre']} (Serie), C={res['c']['nombre']} (Gnd)")
            else:
                print(f"Topologia: Pasa Altas (Entrada +)")
                print(f"Componentes RC: C={res['c']['nombre']} (Serie), R={res['r']['nombre']} (Gnd)")

            print(f"--- Amplificacion ({conf_ganancia['tipo']}) ---")
            if conf_ganancia['rf']:
                print(f"Rf (Salida a In-): {conf_ganancia['rf']['nombre']}")
                print(f"Rg (In- a Gnd):    {conf_ganancia['rg']['nombre']}")
                print(f"Ganancia Real: x{conf_ganancia['g_real']:.2f}")
            else:
                print("Buffer: Conectar Salida directo a In-")

    except ValueError:
        print("[ERROR] Invalido.")


if __name__ == "__main__":
    sistema_experto()