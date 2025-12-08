# logic/filtros.py
import math
from logic.calculos import calcular_par_rc, calcular_par_rl, calcular_par_rlc, calcular_ganancia_opamp


def menu_filtros_principal(motor):
    while True:
        print("\n--- MENU FILTROS ---")
        print("1. Filtros Pasivos RC")
        print("2. Filtros Pasivos RL")
        print("3. Filtros Pasivos RLC")
        print("4. Filtros Activos (Op-Amps)")
        print("0. Volver al Menu Principal")

        cat = input("Seleccione: ")
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