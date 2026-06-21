# Project Valentine - Módulo de Memoria de Corto Plazo
# Este script se encarga de que Valentine recuerde el hilo de la conversación.

class ValentineMemory:
    def __init__(self, limite_memoria=10):
        """
        Inicializa la memoria. 
        limite_memoria: cuántos mensajes del pasado recordará para no saturar la API.
        """
        self.historial = []
        self.limite_memoria = limite_memoria

    def guardar_interaccion(self, usuario, respuesta_valentine, emocion):
        """Guarda lo que dijiste y lo que Valentine respondió junto con su emoción."""
        # Estructuramos la interacción como un diccionario
        interaccion = {
            "usuario": usuario,
            "valentine": respuesta_valentine,
            "emocion": emocion
        }
        
        self.historial.append(interaccion)
        
        # Si superamos el límite, borramos el recuerdo más viejo para ahorrar memoria
        if len(self.historial) > self.limite_memoria:
            self.historial.pop(0)

    def obtener_contexto_para_api(self):
        """Convierte el historial en un formato de texto que la API de Gemini pueda entender."""
        contexto = ""
        for i, intercambio in enumerate(self.historial):
            contexto += f"Usuario: {intercambio['usuario']}\n"
            contexto += f"Valentine (emoción: {intercambio['emocion']}): {intercambio['valentine']}\n"
        return contexto

    def limpiar_memoria(self):
        """Por si quieres reiniciar la conversación desde cero."""
        self.historial = []
        print("[Memory] Recuerdos borrados con éxito.")


# Prueba de ejecución local integrada (Simulación)
if __name__ == "__main__":
    print("=========================================")
    print("💾 SIMULADOR LOCAL DE VALENTINE MEMORY 💾")
    print("=========================================")
    
    memoria = ValentineMemory(limite_memoria=3)
    
    print("--- REGISTRANDO CONVERSACIÓN ---")
    # Turno 1
    memoria.guardar_interaccion("Hola, me llamo Sebas", "¡Hola Sebas! Qué lindo nombre nya~", "feliz")
    # Turno 2
    memoria.guardar_interaccion("Estoy jugando Minecraft", "¡Qué cool! No te olvides de construirme una estatua", "juguetona")
    
    # Ver cómo recuerda las cosas el script
    print("\nMemoria actual de Valentine para enviar a la API:")
    print("------------------------------------------------")
    print(memoria.obtener_contexto_para_api())
