import json
import os
import re


class ProcesadorTexto:
    def __init__(self):
        self.sufijos = {
            'k': 1e3, 'M': 1e6, 'G': 1e9,
            'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12
        }
        self.intenciones = self._cargar_intenciones()

    def _cargar_intenciones(self):
        """Carga la base de datos de intenciones desde JSON"""
        try:
            ruta = os.path.join("data", "intenciones.json")
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("ERROR CRÍTICO: No se encontró data/intenciones.json")
            return {}

    def extraer_parametros(self, texto):
        """Extrae números y unidades (V, A, Hz, Ohm, F, H)"""
        texto = texto.lower()
        datos = {}

        # Regex optimizado para capturar flotantes y sufijos
        patrones = {
            'voltaje': r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(v|volt)',
            'resistencia': r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(ohm|Ω|resistencia)',
            'capacitancia': r'(\d+(?:\.\d+)?)\s*(u|n|p|m)?\s*(f|farad)',
            'inductancia': r'(\d+(?:\.\d+)?)\s*(m|u)?\s*(h|henry)',
            'frecuencia': r'(\d+(?:\.\d+)?)\s*(k|m|g)?\s*(hz|hertz)',
            'corriente': r'(\d+(?:\.\d+)?)\s*(m|u)?\s*(a|amper)'
        }

        for clave, patron in patrones.items():
            match = re.search(patron, texto)
            if match:
                valor = float(match.group(1))
                sufijo = match.group(2) if match.group(2) else ""
                multiplicador = self.sufijos.get(sufijo, 1.0)
                datos[clave] = valor * multiplicador

        return datos

    def identificar_intencion(self, texto):
        """
        Sistema de Scoring (Puntuación):
        1. Analiza cada intención en la base de datos.
        2. Suma puntos si encuentra palabras clave.
        3. Suma puntos extra si encuentra palabras requeridas.
        4. DESCALIFICA totalmente si encuentra una palabra prohibida.
        5. Gana la intención con más puntos.
        """
        texto = texto.lower()
        mejor_intencion = "DESCONOCIDO"
        max_puntaje = 0

        for nombre_intencion, reglas in self.intenciones.items():
            puntaje = 0
            palabras_clave = reglas.get("palabras_clave", [])
            requeridas = reglas.get("palabras_requeridas", [])
            prohibidas = reglas.get("palabras_prohibidas", [])
            prioridad = reglas.get("prioridad", 1)

            # 1. Verificar prohibidas (Filtro "Kill Switch")
            # Si dice "calcular frecuencia" y la intención requiere NO tener "bobina",
            # pero el usuario dijo "bobina", esta intención muere.
            if any(p in texto for p in prohibidas):
                continue

            # 2. Verificar requeridas (Si faltan, la intención no es válida o tiene muy bajo score)
            # Ejemplo: Para "OHM_LED", "led" es clave, pero "resistencia" podría ser requerida.
            matches_req = sum(1 for p in requeridas if p in texto)
            # Si hay lista de requeridas y no encontramos ninguna, penalizamos fuerte o saltamos
            if requeridas and matches_req == 0:
                continue

            puntaje += matches_req * 3  # Las requeridas valen mucho

            # 3. Verificar palabras clave generales
            for palabra in palabras_clave:
                if palabra in texto:
                    puntaje += 2

            # 4. Multiplicador de prioridad (para desempatar)
            puntaje *= prioridad

            if puntaje > max_puntaje:
                max_puntaje = puntaje
                mejor_intencion = nombre_intencion

        # Umbral mínimo para evitar falsos positivos
        if max_puntaje < 2:
            return "DESCONOCIDO"

        return mejor_intencion