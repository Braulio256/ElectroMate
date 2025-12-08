import json
import os


class BuscadorComponentes:
    def __init__(self):
        # --- CARGA DE RESISTENCIAS ---
        try:
            ruta_res = os.path.join("data", "components", "resistencias.json")
            with open(ruta_res, 'r', encoding='utf-8') as f:
                self.db_resistencias = json.load(f)
        except FileNotFoundError:
            print("ADVERTENCIA: No se encontró resistencias.json")
            self.db_resistencias = []

        # --- CARGA DE CAPACITORES ---
        try:
            ruta_cap = os.path.join("data", "components", "capacitores.json")
            with open(ruta_cap, 'r', encoding='utf-8') as f:
                self.db_capacitores = json.load(f)
        except FileNotFoundError:
            print("ADVERTENCIA: No se encontró capacitores.json")
            self.db_capacitores = []

        # --- CARGA DE OP-AMPS ---
        try:
            ruta_opamps = os.path.join("data", "components", "opamps.json")
            with open(ruta_opamps, 'r', encoding='utf-8') as f:
                self.db_opamps = json.load(f)
        except FileNotFoundError:
            print("[ADVERTENCIA] No se encontró opamps.json")
            self.db_opamps = []

        # --- CARGA DE INDUCTORES ---
        try:
            ruta_ind = os.path.join("data", "components", "inductores.json")
            with open(ruta_ind, 'r', encoding='utf-8') as f:
                self.db_inductores = json.load(f)
        except FileNotFoundError:
            print("[ADVERTENCIA] No se encontró inductores.json")
            self.db_inductores = []

    def buscar_resistencia_optima(self, valor_ideal_ohms, potencia_minima_watts):
        # ... (Mantén tu código anterior de resistencias aquí igual que antes) ...
        # Solo asegúrate de que use self.db_resistencias
        candidatos = []
        margen_seguridad = 1.2
        potencia_objetivo = potencia_minima_watts * margen_seguridad

        for componente in self.db_resistencias:
            if componente['parametros']['potencia_watts'] >= potencia_objetivo:
                candidatos.append(componente)

        if not candidatos:
            return None, "No se encontró resistencia adecuada para esa potencia."

        mejor_opcion = min(candidatos, key=lambda x: abs(x['parametros']['valor_ohmios'] - valor_ideal_ohms))
        return mejor_opcion, "Resistor encontrado"

    def buscar_capacitor_optimo(self, valor_ideal_faradios, voltaje_circuito):
        """
        Busca un capacitor.
        Regla de Experto: El voltaje del capacitor debe ser al menos 1.5 veces el voltaje del circuito
        para evitar explosiones o reducción de vida útil.
        """
        candidatos = []

        # Regla de seguridad de voltaje (Margen del 50%)
        margen_voltaje = 1.5
        voltaje_requerido = voltaje_circuito * margen_voltaje

        # Filtramos por voltaje primero
        for cap in self.db_capacitores:
            if cap['parametros']['voltaje_maximo'] >= voltaje_requerido:
                candidatos.append(cap)

        if not candidatos:
            return None, f"PELIGRO: No hay capacitores que soporten {voltaje_requerido}V (Circuito: {voltaje_circuito}V)"

        # Buscamos el valor de capacitancia más cercano
        mejor_opcion = min(candidatos, key=lambda x: abs(x['parametros']['valor_faradios'] - valor_ideal_faradios))

        return mejor_opcion, "Capacitor encontrado"

    def buscar_opamp_apto(self, frecuencia_circuito_hz, voltaje_fuente):
        """
        Busca un Op-Amp que sea lo suficientemente rápido y soporte el voltaje.
        Regla: GBW > 10 * Frecuencia del filtro.
        """
        candidatos = []
        gbw_requerido = frecuencia_circuito_hz * 10

        for opamp in self.db_opamps:
            params = opamp['parametros']

            # Chequeo 1: Voltaje (El opamp debe soportar el voltaje de fuente)
            # Nota: Muchos opamps requieren voltaje dual (+/-), aquí simplificamos chequeando el maximo total
            if voltaje_fuente > params['voltaje_operacion_max']:
                continue

            # Chequeo 2: Velocidad (GBW)
            if params['gbw_hz'] >= gbw_requerido:
                candidatos.append(opamp)

        if not candidatos:
            return None, f"No hay Op-Amps suficientemente rápidos para {frecuencia_circuito_hz}Hz o que soporten {voltaje_fuente}V."

        # Preferencia: Elegir el más barato que cumpla el trabajo
        mejor_opamp = min(candidatos, key=lambda x: x.get('costo_estimado_usd', 100))

        return mejor_opamp, "Op-Amp seleccionado correctamente"

    def buscar_inductor_optimo(self, valor_ideal_henrys, corriente_circuito):
        """
        Busca inductor por valor y asegura que soporte la corriente (Isat).
        Margen de seguridad: 30% extra de corriente.
        """
        candidatos = []
        margen_corriente = 1.3
        i_requerida = corriente_circuito * margen_corriente

        for comp in self.db_inductores:
            # Filtro 1: Corriente de Saturacion
            if comp['parametros']['corriente_max_A'] >= i_requerida:
                candidatos.append(comp)

        if not candidatos:
            return None, f"No hay inductores que soporten {i_requerida:.2f}A"

        # Filtro 2: Valor mas cercano
        mejor_opcion = min(candidatos, key=lambda x: abs(x['parametros']['valor_henrys'] - valor_ideal_henrys))

        return mejor_opcion, "Inductor encontrado"