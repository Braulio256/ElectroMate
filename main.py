import sys
# Importamos desde los nuevos módulos
from logic.buscador import BuscadorComponentes
from logic.procesador import ProcesadorTexto
from logic.interfaz import C_BOT, C_USR, C_SYS, CambioDeContexto

# Importamos los "workers"
import logic.ohm as ohm
import logic.filtros as filtros


def main():
    print("=====================================================")
    print("      ELECTROMATE v4.0 - SISTEMA MODULAR             ")
    print("=====================================================")
    print("Sistema listo. Ejemplo: 'Filtro activo', 'Resistencia led'.")

    motor = BuscadorComponentes()
    procesador = ProcesadorTexto()
    comando_pendiente = None

    while True:
        try:
            if comando_pendiente:
                entrada = comando_pendiente
                comando_pendiente = None
                print(f"{C_SYS} Redirigiendo solicitud: '{entrada}'")
            else:
                entrada = input(f"\n{C_USR} ").strip()

            if entrada.lower() in ["salir", "exit", "shutdown"]:
                print(f"{C_BOT} Finalizando sesión...")
                break

            if not entrada: continue

            intencion = procesador.identificar_intencion(entrada)
            datos = procesador.extraer_parametros(entrada)

            try:
                # --- ENRUTADOR ---
                if intencion == "FILTRO_AMBIGUO":
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
                    print(f"{C_BOT} Solicitud no reconocida.")

            except CambioDeContexto as e:
                if e.nuevo_comando == "cancelar":
                    print(f"{C_SYS} Operación cancelada.")
                else:
                    print(f"{C_SYS} Cambio de contexto detectado...")
                    comando_pendiente = e.nuevo_comando

        except Exception as e:
            print(f"{C_SYS} Error crítico: {e}")


if __name__ == "__main__":
    main()