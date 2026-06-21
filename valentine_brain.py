# Project Valentine - Módulo del Cerebro Emocional
# Este script maneja la lógica de la personalidad y estados de ánimo de Valentine.

import random

class ValentineBrain:
    def __init__(self):
        # Estado emocional inicial de nuestra Neko Avatar
        self.emocion_actual = "Neutral"
        self.nombre_usuario = "Sebas"
        
        # Lista de emociones soportadas por el sistema visual
        self.emociones_disponibles = ["Neutral", "Feliz", "Enojada", "Triste", "Juguetona", "Tímida"]

    def procesar_entrada(self, texto_usuario):
        """
        Simulación de procesamiento de lenguaje.
        En la laptop, aquí se llamará a la API de Gemini (Google AI Studio).
        """
        texto = texto_usuario.lower()
        
        # Sistema básico de reglas para la simulación local
        if "hola" in texto or "buenos días" in texto:
            self.emocion_actual = "Feliz"
            respuesta = f"¡Hola, {self.nombre_usuario}! ¡Qué bueno verte de nuevo nya~!"
            
        elif "error" in texto or "bug" in texto or "no funciona" in texto:
            self.emocion_actual = "Tímida"
            respuesta = "¡Ufff, un bug... lo siento mucho! Déjame ayudarte a revisar el código, ¡no te rindas!"
            
        elif "minecraft" in texto or "jugar" in texto:
            self.emocion_actual = "Juguetona"
            respuesta = "¡Siiii, vamos a jugar! Pero primero terminemos de programar, ¿vale?"
            
        elif "te quiero" in texto or "gracias" in texto:
            self.emocion_actual = "Tímida"
            respuesta = "¡Ah... gracias, Sebas! Yo también disfruto mucho ser tu asistente... *se sonroja*"
            
        else:
            # Si no entiende, elige una emoción aleatoria para la simulación
            self.emocion_actual = random.choice(["Neutral", "Juguetona"])
            respuesta = "Entendido. Estoy analizando lo que pasa en tu pantalla para darte soporte."

        return respuesta, self.emocion_actual

    def forzar_emocion(self, nueva_emocion):
        """Permite que el sistema de visión o audio cambie su emoción directamente."""
        if nueva_emocion in self.emociones_disponibles:
            self.emocion_actual = nueva_emocion
            print(f"[Brain] Emoción cambiada manualmente a: {self.emocion_actual}")
        else:
            print(f"[Brain] Error: La emoción '{nueva_emocion}' no existe en el sistema.")


# Bloque de prueba local (Simulación en consola)
if __name__ == "__main__":
    print("=========================================")
    print("🧠 SIMULADOR LOCAL DE VALENTINE BRAIN 🧠")
    print("=========================================")
    
    brain = ValentineBrain()
    
    pruebas = [
        "¡Hola Valentine!",
        "Tengo un error en el código de Arduino",
        "Quiero ir a jugar Minecraft un rato",
        "Gracias por la ayuda"
    ]
    
    for frase in pruebas:
        print(f"\n👤 Usuario dice: '{frase}'")
        respuesta, emocion = brain.procesar_entrada(frase)
        print(f"🐱 Valentine responde: '{respuesta}'")
        print(f"🎭 Estado de Ánimo (Emoción): [{emocion}]")
        print("-" * 40)
