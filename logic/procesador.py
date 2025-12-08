import re


class ProcesadorTexto:
    def __init__(self):
        self.sufijos = {
            'k': 1e3, 'M': 1e6, 'G': 1e9,
            'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12
        }

    def extraer_parametros(self, texto):
        texto = texto.lower()
        datos = {}

        # Extracciones estándar (V, I, R, F, C, L)
        # ... (Copia las extracciones de V, I, R, F del código anterior) ...
        # Copio las más comunes aquí para referencia:
        match_v = re.search(r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(v|volt)', texto)
        if match_v: datos['voltaje'] = float(match_v.group(1)) * self.sufijos.get(match_v.group(2), 1)

        match_r = re.search(r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(ohm|Ω|resistencia)', texto)
        if match_r: datos['resistencia'] = float(match_r.group(1)) * self.sufijos.get(match_r.group(2), 1)

        match_c = re.search(r'(\d+(?:\.\d+)?)\s*(u|n|p|m)?\s*(f|farad)', texto)
        if match_c: datos['capacitancia'] = float(match_c.group(1)) * self.sufijos.get(match_c.group(2), 1)

        match_l = re.search(r'(\d+(?:\.\d+)?)\s*(m|u)?\s*(h|henry)', texto)
        if match_l: datos['inductancia'] = float(match_l.group(1)) * self.sufijos.get(match_l.group(2), 1)

        return datos

    def identificar_intencion(self, texto):
        t = texto.lower()
        palabras_calc = ["calcula", "calcular", "dime", "saber", "obtener", "cual es", "cuanto es"]

        # --- NUEVO: REDUCCION DE CIRCUITOS ---
        if "serie" in t or "paralelo" in t or "equivalente" in t:
            if "resistencia" in t: return "DC_REQ"
            if "capacito" in t: return "DC_CEQ"
            return "DC_REDUCCION_AMBIGUA"  # Si no dice qué componente es

        # --- NUEVO: TRANSITORIOS (TAU) ---
        if "tau" in t or "constante de tiempo" in t or "carga" in t and ("capacitor" in t or "inductor" in t):
            return "DC_TRANSITORIO"

        # --- FILTROS (MANTENER) ---
        if "frecuencia" in t and any(p in t for p in palabras_calc) and "corte" in t:
            return "FILTRO_CALC_FC_RC"

        if "filtro" in t or "diseña" in t:
            if "activo" in t or "opamp" in t: return "FILTRO_ACTIVO"
            if "rlc" in t or "resonancia" in t: return "FILTRO_RLC"
            if "rl" in t or "inductor" in t: return "FILTRO_RL"
            if "pasa bajo" in t or "pasa bajas" in t: return "FILTRO_LP"
            if "pasa alto" in t or "pasa altas" in t: return "FILTRO_HP"
            if "rechaza" in t or "notch" in t: return "FILTRO_NOTCH"
            return "FILTRO_AMBIGUO"

        # --- LEY DE OHM (MANTENER) ---
        if "divisor" in t and "voltaje" in t: return "OHM_DIVISOR"
        if "energia" in t or "consumo" in t or "bateria" in t: return "OHM_ENERGIA"

        if "led" in t or "limitadora" in t: return "OHM_LED"
        if "voltaje" in t and any(p in t for p in palabras_calc): return "OHM_CALC_V"
        if "corriente" in t and any(p in t for p in palabras_calc): return "OHM_CALC_I"
        if "resistencia" in t and any(p in t for p in palabras_calc): return "OHM_CALC_R"
        if "potencia" in t and any(p in t for p in palabras_calc): return "OHM_CALC_P"

        return "DESCONOCIDO"