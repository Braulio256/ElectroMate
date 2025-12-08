from logic.calculos import (
    calcular_corriente_ohm,
    calcular_voltaje_ohm,
    calcular_potencia_dc,
    calcular_resistencia_limitadora
)


def menu_ley_ohm(motor):
    print("\n--- LEY DE OHM Y POTENCIA ---")
    print("1. Resistencia Limitadora (Proteccion de Cargas)")
    print("2. Calcular Corriente (Tengo V y R)")
    print("3. Calcular Voltaje (Tengo I y R)")
    print("4. Calcular Potencia (Tengo V e I)")

    tipo = input("Seleccione calculo: ")

    try:
        # 1. RESISTENCIA LIMITADORA (GENERALIZADO)
        if tipo == "1":
            print("\n[DISEÑO RESISTENCIA LIMITADORA]")
            print("Sirve para: LEDs, Zener, Motores DC pequeños, Bases de Transistor, etc.")
            v_fuente = float(input("Voltaje de la Fuente (V): "))
            v_carga = float(input("Voltaje nominal de la Carga (V): "))
            i_mA = float(input("Corriente nominal de la Carga (mA): "))

            # Usamos la funcion actualizada de calculos.py
            r_teorica, p_teorica = calcular_resistencia_limitadora(v_fuente, v_carga, i_mA / 1000.0)

            if r_teorica is None:
                print("[ERROR] El voltaje de fuente debe ser MAYOR al de la carga.")
                return

            print(f"-> Resistencia Serie: {r_teorica:.2f} Ω")
            print(f"-> Potencia en Resistencia: {p_teorica:.4f} W")

            comp, msg = motor.buscar_resistencia_optima(r_teorica, p_teorica)
            if comp:
                print(f"✅ SUGERENCIA COMERCIAL: {comp['nombre']}")
                print(
                    f"   (Valor: {comp['parametros']['valor_ohmios']}Ω, Potencia: {comp['parametros']['potencia_watts']}W)")
            else:
                print(f"[ALERTA] {msg}")

        # 2. CALCULAR CORRIENTE
        elif tipo == "2":
            print("\n[CALCULO DE CORRIENTE I=V/R]")
            v = float(input("Voltaje (V): "))
            r = float(input("Resistencia (Ohms): "))

            i_A = calcular_corriente_ohm(v, r)
            if i_A is None:
                print("[ERROR] Resistencia no puede ser 0");
                return

            p_W = calcular_potencia_dc(v, i_A)

            print("-" * 30)
            print(f"⚡ Corriente: {i_A * 1000:.2f} mA ({i_A:.4f} A)")
            print(f"🔥 Potencia:  {p_W:.4f} W")

            comp, msg = motor.buscar_resistencia_optima(r, p_W)
            if comp:
                r_found = comp['parametros']['valor_ohmios']
                if abs(r - r_found) < (r * 0.1):
                    print(f"✅ VIABLE: Existe {comp['nombre']} que soporta esta potencia.")
                else:
                    print(f"⚠️ AVISO: Calculado con {r}Ω. Comercial más cercana: {r_found}Ω.")
            else:
                print(f"❌ ALERTA: No existe resistencia comercial única para {p_W:.2f}W.")

        # 3. CALCULAR VOLTAJE
        elif tipo == "3":
            print("\n[CALCULO DE VOLTAJE V=I*R]")
            i_mA = float(input("Corriente (mA): "))
            r = float(input("Resistencia (Ohms): "))

            i_A = i_mA / 1000.0
            v = calcular_voltaje_ohm(i_A, r)
            p_W = calcular_potencia_dc(v, i_A)

            print("-" * 30)
            print(f"⚡ Voltaje: {v:.2f} V")
            print(f"🔥 Potencia: {p_W:.4f} W")

            comp, msg = motor.buscar_resistencia_optima(r, p_W)
            if not comp: print(f"❌ Alerta: La resistencia {r}Ω se quemaría.")

        # 4. CALCULAR POTENCIA
        elif tipo == "4":
            print("\n[CALCULO DE POTENCIA P=V*I]")
            v = float(input("Voltaje (V): "))
            i_mA = float(input("Corriente (mA): "))

            i_A = i_mA / 1000.0
            p_W = calcular_potencia_dc(v, i_A)

            if i_A > 0:
                r_eq = v / i_A
                print("-" * 30)
                print(f"🔥 Potencia Total: {p_W:.4f} W")
                print(f"💡 Resistencia Equivalente: {r_eq:.2f} Ω")

                comp, msg = motor.buscar_resistencia_optima(r_eq, p_W)
                if comp:
                    print(f"✅ SUGERENCIA: {comp['nombre']}")
                else:
                    print(f"❌ NO ENCONTRADA: {msg}")

    except ValueError:
        print("[ERROR] Ingrese solo numeros validos.")