from logic.buscador import BuscadorComponentes
from logic.procesador import ProcesadorTexto
from logic.interfaz import C_BOT, C_USR, C_SYS, CambioDeContexto
# IMPORTAR EL GESTOR DE AUTENTICACIÓN
from logic.auth import GestorSesion

import logic.ohm as ohm
import logic.filtros as filtros


def main():
    # --- BLOQUE DE SEGURIDAD ---
    sistema_auth = GestorSesion()
    acceso_concedido = sistema_auth.menu_autenticacion()

    if not acceso_concedido:
        return  # Si eligió salir o falló, el programa termina aquí.

    # --- INICIO DEL CHATBOT ---
    print("\n" * 50)  # Limpiar pantalla para efecto "Login Exitoso"
    print("=====================================================")
    print(f"      ELECTROMATE v5.0 - USUARIO: {sistema_auth.usuario_actual.upper()}          ")
    print("=====================================================")
    print("Sistema listo. Módulo experto en Filtros y DC cargado.")

    motor = BuscadorComponentes()
    procesador = ProcesadorTexto()  # Asegúrate de que este archivo tenga la corrección del JSON si la aplicaste
    comando_pendiente = None

    while True:
        try:
            if comando_pendiente:
                entrada = comando_pendiente
                comando_pendiente = None
                print(f"{C_SYS} Redirigiendo: '{entrada}'")
            else:
                entrada = input(f"\n{C_USR} ").strip()

            if entrada.lower() in ["salir", "exit", "shutdown", "cerrar sesion"]:
                print(f"{C_BOT} Guardando sesión... Hasta luego, {sistema_auth.usuario_actual}.")
                break

            if not entrada: continue

            # AQUÍ VA EL RESTO DE TU LÓGICA DE PROCESAMIENTO
            # (Mantén el código que ya tenías dentro del while)
            intencion = procesador.identificar_intencion(entrada)
            datos = procesador.extraer_parametros(entrada)

            try:
                # --- RUTAS DC ---
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

                # --- RUTAS FILTROS (CON O SIN LA LOGICA NUEVA, LA QUE TENGAS) ---
                elif intencion == "FILTRO_AMBIGUO":  # O las nuevas intenciones si usaste el JSON
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

                # --- LEY DE OHM ---
                elif intencion == "OHM_DIVISOR":
                    ohm.resolver_divisor_voltaje(datos, motor)
                elif intencion == "OHM_ENERGIA":
                    ohm.resolver_energia(datos, motor)
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

                # --- NUEVAS RUTAS DE DESAMBIGUACION (SI LAS IMPLEMENTASTE) ---
                elif intencion == "CALCULO_FRECUENCIA_AMBIGUO":
                    filtros.resolver_calculo_frecuencia_ambiguo(datos)
                elif intencion == "FILTRO_DISENO_AMBIGUO":
                    filtros.resolver_filtro_ambiguo_total(datos, motor)

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