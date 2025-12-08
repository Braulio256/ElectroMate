import json
import os


def generar_inductores_comerciales():
    base_datos_inductores = []

    # Serie E6: 1.0, 1.5, 2.2, 3.3, 4.7, 6.8
    base_e6 = [1.0, 1.5, 2.2, 3.3, 4.7, 6.8]
    multiplicadores = [1e-6, 10e-6, 100e-6, 1e-3, 10e-3]  # 1uH a 10mH

    print("Generando base de datos de Inductores...")

    for mult in multiplicadores:
        for base in base_e6:
            valor_h = base * mult

            # --- TIPO 1: AXIAL (Baja corriente, parece resistencia) ---
            # Ideal para filtros de señal pequeños
            nombre_val = ""
            if valor_h < 1e-3:
                nombre_val = f"{valor_h * 1e6:.1f}uH"
            else:
                nombre_val = f"{valor_h * 1e3:.1f}mH"

            ind_axial = {
                "id": f"IND_AXIAL_{nombre_val}",
                "nombre": f"Inductor Axial {nombre_val}",
                "tipo": "Inductive",
                "subtipo": "Axial Color Code",
                "parametros": {
                    "valor_henrys": valor_h,
                    "corriente_max_A": 0.25,  # 250mA tipico
                    "dcr_ohms": 0.5 + (valor_h * 1000),  # DCR simulada (sube con la inductancia)
                    "frecuencia_resonancia_hz": 1_000_000  # Solo referencia
                },
                "costo_estimado_usd": 0.15
            }
            base_datos_inductores.append(ind_axial)

            # --- TIPO 2: BOBINA DE POTENCIA (Power Inductor) ---
            # Ideal para filtrado de fuentes
            ind_power = {
                "id": f"IND_PWR_{nombre_val}",
                "nombre": f"Bobina Potencia {nombre_val}",
                "tipo": "Inductive",
                "subtipo": "Ferrite Core / Toroid",
                "parametros": {
                    "valor_henrys": valor_h,
                    "corriente_max_A": 2.0,  # 2 Amperios
                    "dcr_ohms": 0.05 + (valor_h * 100),  # Mucho menor resistencia
                    "frecuencia_resonancia_hz": 500_000
                },
                "costo_estimado_usd": 0.85
            }
            base_datos_inductores.append(ind_power)

    # Guardar
    ruta_carpeta = os.path.join("data", "components")
    os.makedirs(ruta_carpeta, exist_ok=True)
    ruta_archivo = os.path.join(ruta_carpeta, "inductores.json")

    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(base_datos_inductores, f, indent=2, ensure_ascii=False)

    print(f"Listo. 'inductores.json' generado con {len(base_datos_inductores)} componentes.")


if __name__ == "__main__":
    generar_inductores_comerciales()