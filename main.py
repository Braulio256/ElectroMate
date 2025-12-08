from logic.buscador import BuscadorComponentes
from logic.ohm import menu_ley_ohm
from logic.filtros import menu_filtros_principal


def sistema_experto():
    print("=== SISTEMA EXPERTO DE DISENO ELECTRONICO v4.0 (Modular) ===")

    # Inicializamos la base de datos una sola vez
    motor = BuscadorComponentes()

    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1. Ley de Ohm y Potencia")
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


if __name__ == "__main__":
    sistema_experto()