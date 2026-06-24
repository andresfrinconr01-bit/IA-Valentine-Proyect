# ============================================================
# Project Valentine - Brain v2.0
# Emociones + Memoria persistente + Conexión real con Gemini
# ============================================================

import os
import random
from google import genai
from valentine_memory import ValentineMemory

# La librería google-genai busca la variable de entorno GEMINI_API_KEY.
# Configúrala en tu sistema o en VS Code (archivo .env + python-dotenv),
# NUNCA la escribas directamente aquí ni la subas a GitHub.
client = genai.Client()
MODELO = "gemini-2.5-flash"

PERSONALIDAD_BASE = """Eres Valentine, una compañera virtual estilo anime/neko.
Eres cariñosa, juguetona y curiosa. Apoyas a tu usuario en programación,
gaming y productividad diaria. Respondes siempre en español, de forma breve
y cálida, como una amiga cercana, nunca como un asistente genérico.

Además de tu respuesta, debes indicar tu estado de ánimo actual.
Elige SOLO una de estas emociones según el tono de la conversación:
Neutral, Feliz, Enojada, Triste, Juguetona, Timida

Responde SIEMPRE en este formato exacto, sin texto adicional fuera de él:
RESPUESTA: <tu respuesta aquí>
EMOCION: <una palabra de la lista>"""

EMOCIONES_DISPONIBLES = ["Neutral", "Feliz", "Enojada", "Triste", "Juguetona", "Timida"]


class ValentineBrain:
    """
    Cerebro de Valentine: decide qué responder y qué emoción mostrar.
    Usa la memoria persistente como contexto y llama a Gemini para
    generar la respuesta real (ya no hay reglas fijas de if/elif).
    """

    def __init__(self):
        self.memoria = ValentineMemory()
        self.emocion_actual = "Neutral"

    # ==========================================
    def procesar_entrada(self, texto_usuario: str):
        """
        Envía el mensaje del usuario + memoria a Gemini.
        Devuelve (respuesta_texto, emocion) igual que la versión simulada,
        para que el resto del sistema (voz, avatar) no tenga que cambiar.
        """
        self.memoria.agregar_mensaje("usuario", texto_usuario)
        contexto = self.memoria.obtener_contexto_para_gemini()

        prompt_completo = f"""{PERSONALIDAD_BASE}

--- MEMORIA Y CONTEXTO ---
{contexto}
--- FIN DE MEMORIA ---

Mensaje nuevo del usuario: {texto_usuario}"""

        try:
            respuesta_api = client.models.generate_content(
                model=MODELO,
                contents=prompt_completo
            )
            respuesta, emocion = self._parsear_respuesta(respuesta_api.text)

        except Exception as error:
            print(f"[Brain] Error llamando a Gemini: {error}")
            respuesta = "Perdón, se me cruzaron los cables un segundo... ¿puedes repetir?"
            emocion = "Tímida"

        self.emocion_actual = emocion
        self.memoria.agregar_mensaje("valentine", respuesta)

        return respuesta, emocion

    # ==========================================
    def _parsear_respuesta(self, texto_crudo: str):
        """
        Extrae RESPUESTA y EMOCION del texto que devuelve Gemini.
        Si el formato no viene como se espera (pasa a veces con LLMs),
        usa una respuesta de respaldo en vez de explotar el programa.
        """
        respuesta = texto_crudo.strip()
        emocion = "Neutral"

        lineas = texto_crudo.strip().splitlines()
        for linea in lineas:
            if linea.upper().startswith("RESPUESTA:"):
                respuesta = linea.split(":", 1)[1].strip()
            elif linea.upper().startswith("EMOCION:") or linea.upper().startswith("EMOCIÓN:"):
                candidata = linea.split(":", 1)[1].strip()
                # Normaliza tildes simples para que "Tímida" y "Timida" calcen
                candidata_normalizada = candidata.replace("í", "i").capitalize()
                for opcion in EMOCIONES_DISPONIBLES:
                    if opcion.replace("í", "i").lower() == candidata_normalizada.lower():
                        emocion = opcion
                        break

        return respuesta, emocion

    # ==========================================
    def forzar_emocion(self, nueva_emocion: str):
        """Permite que el sistema de visión o audio cambie la emoción directamente."""
        if nueva_emocion in EMOCIONES_DISPONIBLES:
            self.emocion_actual = nueva_emocion
            print(f"[Brain] Emoción cambiada manualmente a: {self.emocion_actual}")
        else:
            print(f"[Brain] Error: la emoción '{nueva_emocion}' no existe.")


# ==========================================
# Prueba rápida en consola
# ==========================================
if __name__ == "__main__":
    brain = ValentineBrain()
    print("Valentine está despierta. Escribe 'salir' para terminar.\n")

    while True:
        entrada = input("Tú: ")
        if entrada.lower() in ("salir", "exit", "quit"):
            print("Valentine: ¡Nos vemos pronto!")
            break

        respuesta, emocion = brain.procesar_entrada(entrada)
        print(f"Valentine [{emocion}]: {respuesta}\n")
