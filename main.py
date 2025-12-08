from logic.buscador import BuscadorComponentes
from logic.procesador import ProcesadorTexto
from logic.interfaz import C_BOT, C_USR, C_SYS, CambioDeContexto

import logic.ohm as ohm
import logic.filtros as filtros


def main():
    print("=====================================================")
    print("      ELECTROMATE v5.0 - SISTEMA EXPERTO DC          ")
    print("=====================================================")
    print("Sistema listo. Capacidades expandidas:")
    print(" - Circuitos DC: Serie/Paralelo, Divisores, Potencia.")
    print(" - Análisis: Transitorios (Tau), Carga de capacitores.")
    print(" - Diseño: Filtros Activos y Pasivos, Ley de Ohm.")

    motor = BuscadorComponentes()
    procesador = ProcesadorTexto()
    comando_pendiente = None

    while True:
        try:
            if comando_pendiente:
                entrada = comando_pendiente
                comando_pendiente = None
                print(f"{C_SYS} Redirigiendo: '{entrada}'")
            else:
                entrada = input(f"\n{C_USR} ").strip()

            if entrada.lower() in ["salir", "exit", "shutdown"]:
                print(f"{C_BOT} Guardando sesión... Hasta luego.")
                break

            if not entrada: continue

            intencion = procesador.identificar_intencion(entrada)
            datos = procesador.extraer_parametros(entrada)

            try:
                # --- NUEVAS RUTAS DC ---
                if intencion == "DC_REQ":
                    ohm.resolver_reduccion_resistencias(datos, motor)
                elif intencion == "DC_CEQ":
                    ohm.resolver_reduccion_capacitores(datos, motor)
                elif intencion == "DC_TRANSITORIO":
                    ohm.resolver_transitorio_tau(datos, motor)
                elif intencion == "DC_REDUCCION_AMBIGUA":
                    print(f"{C_BOT} ¿Quieres calcular equivalentes de Resistencias o Capacitores?")
                    resp = input(f"{C_USR} ").lower()
                    if "cap" in resp:
                        ohm.resolver_reduccion_capacitores(datos, motor)
                    else:
                        ohm.resolver_reduccion_resistencias(datos, motor)

                # --- RUTAS EXISTENTES ---
                elif intencion == "OHM_DIVISOR":
                    ohm.resolver_divisor_voltaje(datos, motor)
                elif intencion == "OHM_ENERGIA":
                    ohm.resolver_energia(datos, motor)

                # Filtros
                elif intencion == "FILTRO_AMBIGUO":
                    filtros.resolver_filtro_ambiguo(datos, motor)
                elif intencion == "FILTRO_ACTIVO":
                    filtros.resolver_filtro_activo(datos, motor)
                elif intencion == "FILTRO_RL":
                    filtros.resolver_filtro_rl(datos, motor)
                elif intencion == "FILTRO_RLC":
                    filtros.resolver_filtro_rlc(datos, motor)
                elif intencion in ["FILTRO_LP", "FILTRO_HP", "FILTRO_NOTCH"]:
                    tipo = intencion.replace("FILTRO_", "")
                    filtros.resolver_filtro_rc(datos, motor, tipo)
                elif intencion == "FILTRO_CALC_FC_RC":
                    filtros.resolver_calc_fc_rc(datos)

                # Ohm Básico
                elif intencion == "OHM_CALC_V":
                    ohm.resolver_voltaje(datos, motor)
                elif intencion == "OHM_CALC_I":
                    ohm.resolver_corriente(datos, motor)
                elif intencion == "OHM_CALC_R":
                    ohm.resolver_resistencia(datos, motor)
                elif intencion == "OHM_CALC_P":
                    ohm.resolver_potencia(datos, motor)
                elif intencion == "OHM_LED":
                    ohm.resolver_led(datos, motor)

                else:
                    print(f"{C_BOT} No estoy seguro de qué necesitas.")
                    print("       Prueba: 'Resistencias en paralelo', 'Constante de tiempo', 'Filtro activo'.")

            except CambioDeContexto as e:
                if e.nuevo_comando == "cancelar":
                    print(f"{C_SYS} Operación cancelada.")
                else:
                    comando_pendiente = e.nuevo_comando

        except Exception as e:
            print(f"{C_SYS} Error crítico: {e}")


if __name__ == "__main__":
    main()