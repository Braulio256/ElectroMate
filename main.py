import os
from logic.buscador import BuscadorComponentes
from logic.interfaz import C_BOT, C_USR, C_SYS, CambioDeContexto
# Importamos el sistema de seguridad
from logic.auth import GestorSesion

# Importamos la lógica de cálculo
import logic.ohm as ohm
import logic.filtros as filtros


def limpiar_pantalla():
    # Detecta si es Windows (nt) o Linux/Mac (posix)
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_cabecera(usuario):
    limpiar_pantalla()
    print("=====================================================")
    print(f"      ELECTROMATE v5.0 - USUARIO: {usuario.upper()}      ")
    print("=====================================================")
    print("             MODO: MENÚ INTERACTIVO                  ")
    print("=====================================================\n")


# --- SUBMENÚS ---

def menu_ley_ohm(motor):
    while True:
        print(f"\n{C_BOT} --- LEY DE OHM Y POTENCIA DC ---")
        print(" [1] Calcular Voltaje (V = I * R)")
        print(" [2] Calcular Corriente (I = V / R)")
        print(" [3] Calcular Resistencia (R = V / I)")
        print(" [4] Calcular Potencia (P = V * I)")
        print(" [5] Divisor de Voltaje")
        print(" [6] Cálculo Resistencia para LED")
        print(" [7] Cálculo de Energía / Batería")
        print(" [0] Volver al Menú Principal")

        op = input(f"\n{C_USR} Elige una opción: ").strip()

        # Al pasar datos={}, forzamos a que el programa pregunte los valores
        datos_vacios = {}

        try:
            if op == "1":
                ohm.resolver_voltaje(datos_vacios, motor)
            elif op == "2":
                ohm.resolver_corriente(datos_vacios, motor)
            elif op == "3":
                ohm.resolver_resistencia(datos_vacios, motor)
            elif op == "4":
                ohm.resolver_potencia(datos_vacios, motor)
            elif op == "5":
                ohm.resolver_divisor_voltaje(datos_vacios, motor)
            elif op == "6":
                ohm.resolver_led(datos_vacios, motor)
            elif op == "7":
                ohm.resolver_energia(datos_vacios, motor)
            elif op == "0":
                break
            else:
                print(f"{C_SYS} Opción inválida.")
        except CambioDeContexto:
            print(f"{C_SYS} Operación cancelada.")

        input(f"\n{C_SYS} Presiona ENTER para continuar...")


def menu_circuitos(motor):
    while True:
        print(f"\n{C_BOT} --- ANÁLISIS DE CIRCUITOS ---")
        print(" [1] Resistencia Equivalente (Serie/Paralelo)")
        print(" [2] Capacitancia Equivalente (Serie/Paralelo)")
        print(" [3] Análisis Transitorio (Tau - Carga/Descarga)")
        print(" [0] Volver al Menú Principal")

        op = input(f"\n{C_USR} Elige una opción: ").strip()
        datos_vacios = {}

        try:
            if op == "1":
                ohm.resolver_reduccion_resistencias(datos_vacios, motor)
            elif op == "2":
                ohm.resolver_reduccion_capacitores(datos_vacios, motor)
            elif op == "3":
                ohm.resolver_transitorio_tau(datos_vacios, motor)
            elif op == "0":
                break
            else:
                print(f"{C_SYS} Opción inválida.")
        except CambioDeContexto:
            print(f"{C_SYS} Operación cancelada.")

        input(f"\n{C_SYS} Presiona ENTER para continuar...")


def menu_filtros_diseno(motor):
    while True:
        print(f"\n{C_BOT} --- DISEÑO DE FILTROS (Buscar Componentes) ---")
        print(" [1] Filtro Pasivo RC - Pasa Bajas")
        print(" [2] Filtro Pasivo RC - Pasa Altas")
        print(" [3] Filtro Pasivo RC - Notch (Rechaza Banda)")
        print(" [4] Filtro Activo (Op-Amp)")
        print(" [5] Filtro RL (Inductivo - Potencia)")
        print(" [6] Filtro RLC (Resonante)")
        print(" [0] Volver al Menú Principal")

        op = input(f"\n{C_USR} Elige una opción: ").strip()
        datos_vacios = {}

        try:
            if op == "1":
                filtros.resolver_filtro_rc(datos_vacios, motor, "LP")
            elif op == "2":
                filtros.resolver_filtro_rc(datos_vacios, motor, "HP")
            elif op == "3":
                filtros.resolver_filtro_rc(datos_vacios, motor, "NOTCH")
            elif op == "4":
                filtros.resolver_filtro_activo(datos_vacios, motor)
            elif op == "5":
                filtros.resolver_filtro_rl(datos_vacios, motor)
            elif op == "6":
                filtros.resolver_filtro_rlc(datos_vacios, motor)
            elif op == "0":
                break
            else:
                print(f"{C_SYS} Opción inválida.")
        except CambioDeContexto:
            print(f"{C_SYS} Operación cancelada.")

        input(f"\n{C_SYS} Presiona ENTER para continuar...")


def menu_calculadoras(motor):
    while True:
        print(f"\n{C_BOT} --- CALCULADORAS RÁPIDAS (Sin búsqueda) ---")
        print(" [1] Calcular Frecuencia de Corte (Circuito RC)")
        print(" [2] Calcular Frecuencia de Corte (Circuito RL)")
        print(" [3] Calcular Frecuencia Resonancia (Circuito LC/RLC)")
        print(" [0] Volver al Menú Principal")

        op = input(f"\n{C_USR} Elige una opción: ").strip()
        datos_vacios = {}

        try:
            if op == "1":
                filtros.resolver_calc_fc_rc(datos_vacios)
            elif op == "2":
                filtros.resolver_calc_fc_rl(datos_vacios)
            elif op == "3":
                filtros.resolver_calc_fc_rlc(datos_vacios)
            elif op == "0":
                break
            else:
                print(f"{C_SYS} Opción inválida.")
        except CambioDeContexto:
            print(f"{C_SYS} Operación cancelada.")

        input(f"\n{C_SYS} Presiona ENTER para continuar...")


# --- MENU PRINCIPAL ---

def main():
    # 1. BLOQUE DE SEGURIDAD
    sistema_auth = GestorSesion()
    acceso_concedido = sistema_auth.menu_autenticacion()

    if not acceso_concedido:
        return

        # 2. CARGA DEL SISTEMA
    mostrar_cabecera(sistema_auth.usuario_actual)
    print("Cargando base de datos de componentes...")
    motor = BuscadorComponentes()
    print("Sistema cargado correctamente.\n")

    # 3. BUCLE PRINCIPAL
    while True:
        mostrar_cabecera(sistema_auth.usuario_actual)
        print(" SELECCIONE UN MÓDULO:")
        print(" [1] Ley de Ohm y Potencia DC")
        print(" [2] Circuitos y Reducciones (Req, Ceq, Tau)")
        print(" [3] Diseño de Filtros (Busca componentes)")
        print(" [4] Calculadoras de Frecuencia (Solo fórmulas)")
        print(" [0] Cerrar Sesión y Salir")

        opcion_principal = input(f"\n{C_USR} Opción: ").strip()

        if opcion_principal == "1":
            menu_ley_ohm(motor)
        elif opcion_principal == "2":
            menu_circuitos(motor)
        elif opcion_principal == "3":
            menu_filtros_diseno(motor)
        elif opcion_principal == "4":
            menu_calculadoras(motor)
        elif opcion_principal == "0":
            print(f"\n{C_BOT} Cerrando sesión... ¡Hasta pronto, {sistema_auth.usuario_actual}!")
            break
        else:
            print(f"{C_SYS} Opción no válida.")
            input("Presiona ENTER...")


if __name__ == "__main__":
    main()