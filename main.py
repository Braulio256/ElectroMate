import math
from logic.buscador import BuscadorComponentes


def sistema_experto():
    print("=== SISTEMA EXPERTO DE DISENO ELECTRONICO v3.1 (Correccion Ley Ohm) ===")
    motor = BuscadorComponentes()

    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1. Ley de Ohm y Potencia (Analisis DC)")
        print("2. Disenar Filtros (Suite Completa)")
        print("0. Salir")

        opcion = input("Seleccione una opcion: ")

        if opcion == "1":
            menu_ley_ohm(motor)
        elif opcion == "2":
            menu_filtros_principal(motor)
        elif opcion == "0":
            print("Cerrando sistema...")
            break
        else:
            print("[ERROR] Opcion no valida.")


# --- MENU LEY DE OHM MEJORADO ---
def menu_ley_ohm(motor):
    print("\n--- LEY DE OHM Y POTENCIA ---")
    print("1. Resistencia Limitadora (Para LEDs)")
    print("2. Calcular Corriente (Tengo V y R)")
    print("3. Calcular Voltaje (Tengo I y R)")
    print("4. Calcular Potencia (Tengo V e I)")

    tipo = input("Seleccione calculo: ")

    try:
        # --- 1. RESISTENCIA LIMITADORA ---
        if tipo == "1":
            print("\n[DISEÑO LIMITADORA LED]")
            v_fuente = float(input("Voltaje Fuente (V): "))
            v_led = float(input("Voltaje LED (V): "))
            i_mA = float(input("Corriente LED (mA): "))

            if v_fuente <= v_led:
                print("[ERROR] La fuente debe ser mayor al voltaje del LED.")
                return

            i_A = i_mA / 1000.0
            r_teorica = (v_fuente - v_led) / i_A
            p_teorica = (v_fuente - v_led) * i_A

            print(f"-> R Calculada: {r_teorica:.2f} Ω")
            print(f"-> P Disipada:  {p_teorica:.4f} W")

            comp, msg = motor.buscar_resistencia_optima(r_teorica, p_teorica)
            if comp:
                print(f"✅ SUGERENCIA COMERCIAL: {comp['nombre']}")
                print(
                    f"   (Valor: {comp['parametros']['valor_ohmios']}Ω, Potencia: {comp['parametros']['potencia_watts']}W)")
            else:
                print(f"[ALERTA] {msg}")

        # --- 2. CALCULAR CORRIENTE ---
        elif tipo == "2":
            print("\n[CALCULO DE CORRIENTE I=V/R]")
            v = float(input("Voltaje (V): "))
            r = float(input("Resistencia (Ohms): "))

            if r <= 0: print("[ERROR] R > 0"); return

            i_A = v / r
            p_W = (v ** 2) / r

            print("-" * 30)
            print(f"⚡ Corriente: {i_A * 1000:.2f} mA ({i_A:.4f} A)")
            print(f"🔥 Potencia:  {p_W:.4f} W")

            # Buscamos si la resistencia que el usuario ingresó existe comercialmente para esa potencia
            print("... Verificando viabilidad del componente ...")
            comp, msg = motor.buscar_resistencia_optima(r, p_W)

            if comp:
                # Verificamos si el valor óhmico es cercano al que ingresó el usuario
                r_found = comp['parametros']['valor_ohmios']
                if abs(r - r_found) < (r * 0.1):  # 10% tolerancia
                    print(f"✅ VIABLE: Existe {comp['nombre']} que soporta esta potencia.")
                else:
                    print(f"⚠️ CUIDADO: Ingresaste {r}Ω, pero el valor comercial más cercano es {r_found}Ω.")
                    print(f"   Sugerencia: Usa la de {comp['nombre']}.")
            else:
                print(f"❌ PELIGRO: No encontré una resistencia comercial única que soporte {p_W:.2f}W.")
                print("   Solución: Usa resistencias de potencia (cerámica) o conéctalas en paralelo.")

        # --- 3. CALCULAR VOLTAJE ---
        elif tipo == "3":
            print("\n[CALCULO DE VOLTAJE V=I*R]")
            i_mA = float(input("Corriente (mA): "))
            r = float(input("Resistencia (Ohms): "))

            i_A = i_mA / 1000.0
            v = i_A * r
            p_W = (i_A ** 2) * r

            print("-" * 30)
            print(f"⚡ Voltaje: {v:.2f} V")
            print(f"🔥 Potencia: {p_W:.4f} W")

            comp, msg = motor.buscar_resistencia_optima(r, p_W)
            if comp:
                print(f"✅ Componente adecuado: {comp['nombre']}")
            else:
                print(f"❌ Alerta de Potencia: {msg}")

        # --- 4. CALCULAR POTENCIA ---
        elif tipo == "4":
            print("\n[CALCULO DE POTENCIA P=V*I]")
            v = float(input("Voltaje (V): "))
            i_mA = float(input("Corriente (mA): "))

            i_A = i_mA / 1000.0
            p_W = v * i_A

            if i_A > 0:
                r_eq = v / i_A
                print("-" * 30)
                print(f"🔥 Potencia Total: {p_W:.4f} W")
                print(f"💡 Resistencia Equivalente: {r_eq:.2f} Ω")

                print("... Buscando resistencia comercial ...")
                comp, msg = motor.buscar_resistencia_optima(r_eq, p_W)

                if comp:
                    r_real = comp['parametros']['valor_ohmios']
                    print(f"✅ SUGERENCIA COMERCIAL: {comp['nombre']}")
                    print(f"   ID: {comp['id']}")

                    # Mostrar diferencia si el valor calculado no es estandar
                    if r_real != r_eq:
                        diff = abs(r_real - r_eq)
                        print(f"   (Nota: El valor comercial difiere en {diff:.2f}Ω del calculado)")
                else:
                    print(f"❌ NO ENCONTRADA: {msg}")
                    print("   Causa probable: La potencia es > 5W o el valor óhmico es muy bajo/alto.")
            else:
                print("[INFO] Sin corriente no hay potencia.")

    except ValueError:
        print("[ERROR] Ingrese solo numeros validos.")


# --- FUNCIONES DE CALCULO FILTROS (Sin cambios) ---
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


# --- MENUS Y SUBMENUS ---
def menu_filtros_principal(motor):
    print("\n--- CATEGORIA DE FILTROS ---")
    print("1. Filtros Pasivos RC")
    print("2. Filtros Pasivos RL")
    print("3. Filtros Pasivos RLC")
    print("4. Filtros Activos (Op-Amps)")
    print("0. Volver")
    cat = input("Seleccione: ")
    if cat == "1":
        menu_filtros_rc(motor)
    elif cat == "2":
        menu_filtros_rl(motor)
    elif cat == "3":
        menu_filtros_rlc(motor)
    elif cat == "4":
        menu_filtros_activos(motor)


def menu_filtros_rc(motor):
    print("\n--- FILTROS PASIVOS RC ---")
    print("1. Pasa Bajas")
    print("2. Pasa Altas")
    print("3. Rechaza Banda")
    print("4. Pasa Banda")
    print("5. CALC: Freq")
    tipo = input("Seleccione: ")
    if tipo not in ["1", "2", "3", "4", "5"]: return
    try:
        if tipo == "5":
            r = float(input("R (Ohms): "));
            c = float(input("C (uF): "))
            print(f"✅ Freq: {1 / (2 * math.pi * r * (c / 1e6)):.2f} Hz")
            return
        v = float(input("Voltaje (V): "))
        if tipo == "4":
            fb = float(input("Fq Baja: "));
            fa = float(input("Fq Alta: "))
            hp = calcular_par_rc(motor, fb, v);
            lp = calcular_par_rc(motor, fa, v, "bajo")
            if hp and lp: print(
                f"HP: C={hp['c']['nombre']}, R={hp['r']['nombre']}\nLP: R={lp['r']['nombre']}, C={lp['c']['nombre']}")
            return
        f = float(input("Frecuencia (Hz): "))
        res = calcular_par_rc(motor, f, v)
        if res:
            print(f"\n[RC CALCULADO] Freq: {res['f']:.1f}Hz")
            if tipo == "1":
                print(f"LP: R={res['r']['nombre']} -> C={res['c']['nombre']}")
            elif tipo == "2":
                print(f"HP: C={res['c']['nombre']} -> R={res['r']['nombre']}")
            elif tipo == "3":
                print("Twin-T: Ver esquema.")
        else:
            print("[FALLO]")
    except ValueError:
        print("[ERROR]")


def menu_filtros_rl(motor):
    print("\n--- FILTROS PASIVOS RL ---")
    print("1. Pasa Bajas")
    print("2. Pasa Altas")
    print("3. Pasa Banda")
    print("4. CALC: Freq")
    tipo = input("Seleccione: ")
    if tipo not in ["1", "2", "3", "4"]: return
    try:
        if tipo == "4":
            r = float(input("R: "));
            l = float(input("L (mH): "))
            print(f"✅ Freq: {r / (2 * math.pi * (l / 1000)):.2f} Hz");
            return
        i = float(input("Corriente (A): "))
        if tipo == "3":
            fb = float(input("Fq Baja: "));
            fa = float(input("Fq Alta: "))
            hp = calcular_par_rl(motor, fb, i);
            lp = calcular_par_rl(motor, fa, i)
            if hp and lp: print(
                f"HP: R={hp['r']['nombre']}, L={hp['l']['nombre']}\nLP: L={lp['l']['nombre']}, R={lp['r']['nombre']}")
            return
        f = float(input("Frecuencia: "))
        res = calcular_par_rl(motor, f, i)
        if res:
            if tipo == "1":
                print(f"LP: L={res['l']['nombre']} -> R={res['r']['nombre']}")
            else:
                print(f"HP: R={res['r']['nombre']} -> L={res['l']['nombre']}")
        else:
            print("[FALLO]")
    except ValueError:
        print("[ERROR]")


def menu_filtros_rlc(motor):
    print("\n--- FILTROS RLC ---")
    print("1. Pasa Banda")
    print("2. Rechaza Banda")
    print("3. CALC: Freq")
    tipo = input("Seleccione: ")
    if tipo not in ["1", "2", "3"]: return
    try:
        if tipo == "3":
            l = float(input("L (mH): ")) / 1000;
            c = float(input("C (uF): ")) / 1e6
            print(f"✅ Freq: {1 / (2 * math.pi * math.sqrt(l * c)):.2f} Hz");
            return
        f = float(input("Frecuencia: "));
        v = float(input("Voltaje: "))
        res = calcular_par_rlc(motor, f, v)
        if res:
            xl = 2 * math.pi * f * res['l']['parametros']['valor_henrys'];
            r_ideal = xl / 10
            r_com, _ = motor.buscar_resistencia_optima(r_ideal, 0.25)
            print(f"LC: {res['l']['nombre']} + {res['c']['nombre']}")
            print(f"R Sugerida (Q=10): {r_ideal:.1f} ohm")
            if r_com: print(f"-> Comercial: {r_com['nombre']}")
        else:
            print("[FALLO]")
    except ValueError:
        print("[ERROR]")


def menu_filtros_activos(motor):
    print("\n--- FILTROS ACTIVOS ---")
    print("1. Pasa Bajas")
    print("2. Pasa Altas")
    print("3. Pasa Banda")
    print("4. Rechaza Banda")
    tipo = input("Seleccione: ")
    if tipo not in ["1", "2", "3", "4"]: return
    try:
        v = float(input("Voltaje OpAmp: "))
        g_in = input("Ganancia [Enter=1]: ")
        ganancia = float(g_in) if g_in.strip() else 1.0
        conf_g = calcular_ganancia_opamp(motor, ganancia)

        if tipo == "3":
            fb = float(input("Fq Baja: "));
            fa = float(input("Fq Alta: "))
            hp = calcular_par_rc(motor, fb, v);
            lp = calcular_par_rc(motor, fa, v, "bajo")
            op, _ = motor.buscar_opamp_apto(fa, v)
            if hp and lp and op:
                print(
                    f"Chip: {op['nombre']}\nHP: C={hp['c']['nombre']}, R={hp['r']['nombre']}\nLP: R={lp['r']['nombre']}, C={lp['c']['nombre']}")
                if conf_g['rf']: print(
                    f"Ganancia x{conf_g['g_real']:.1f}: Rf={conf_g['rf']['nombre']}, Rg={conf_g['rg']['nombre']}")
            return

        if tipo == "4":
            f = float(input("Freq Notch: "));
            res = calcular_par_rc(motor, f, v);
            op, _ = motor.buscar_opamp_apto(f, v)
            if res and op:
                print(
                    f"Notch {op['nombre']}\nRama T-LP: 2x {res['r']['nombre']} Serie, 2x {res['c']['nombre']} Paralelo a Gnd")
                print(f"Rama T-HP: 2x {res['c']['nombre']} Serie, 2x {res['r']['nombre']} Paralelo a Gnd")
            return

        f = float(input("Frecuencia: "))
        res = calcular_par_rc(motor, f, v);
        op, _ = motor.buscar_opamp_apto(f, v)
        if res and op:
            print(f"Chip: {op['nombre']}")
            if tipo == "1":
                print(f"LP: R={res['r']['nombre']}, C={res['c']['nombre']}")
            else:
                print(f"HP: C={res['c']['nombre']}, R={res['r']['nombre']}")
            if conf_g['rf']: print(
                f"Ganancia x{conf_g['g_real']:.1f}: Rf={conf_g['rf']['nombre']}, Rg={conf_g['rg']['nombre']}")
    except ValueError:
        print("[ERROR]")


if __name__ == "__main__":
    sistema_experto()