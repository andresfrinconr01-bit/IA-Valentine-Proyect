# ============================================================
# Project Valentine - Voice v1.0
# Escucha (Speech-to-Text) y habla (Text-to-Speech)
# ============================================================

# Requiere: pip install SpeechRecognition pyttsx3 pyaudio
# Nota sobre pyaudio: en Windows normalmente se instala sin problema con pip.
# En Linux/Mac puede pedir antes: sudo apt install portaudio19-dev (Linux)
#                                  brew install portaudio (Mac)

import speech_recognition as sr
import pyttsx3


class ValentineVoice:
    """
    Maneja la entrada de voz del usuario (micrófono -> texto)
    y la salida de voz de Valentine (texto -> audio hablado).
    """

    def __init__(self, idioma_escucha="es-ES", velocidad_habla=180):
        self.reconocedor = sr.Recognizer()
        self.idioma_escucha = idioma_escucha

        self.motor_voz = pyttsx3.init()
        self.motor_voz.setProperty("rate", velocidad_habla)
        self._configurar_voz_femenina()

    def _configurar_voz_femenina(self):
        """Intenta elegir una voz femenina/española si el sistema tiene una disponible."""
        voces = self.motor_voz.getProperty("voices")
        for voz in voces:
            nombre = voz.name.lower()
            if "spanish" in nombre or "español" in nombre or "female" in nombre:
                self.motor_voz.setProperty("voice", voz.id)
                break

    # ==========================================
    def escuchar(self, duracion_max_segundos=8) -> str:
        """
        Activa el micrófono y transcribe lo que diga el usuario.
        Devuelve el texto transcrito, o "" si no entendió nada.
        """
        with sr.Microphone() as fuente:
            print("[Voice] Escuchando...")
            self.reconocedor.adjust_for_ambient_noise(fuente, duration=0.5)
            try:
                audio = self.reconocedor.listen(fuente, timeout=duracion_max_segundos)
            except sr.WaitTimeoutError:
                print("[Voice] No se detectó audio a tiempo.")
                return ""

        try:
            texto = self.reconocedor.recognize_google(audio, language=self.idioma_escucha)
            print(f"[Voice] Usuario dijo: {texto}")
            return texto

        except sr.UnknownValueError:
            print("[Voice] No se entendió el audio.")
            return ""
        except sr.RequestError as error:
            print(f"[Voice] Error con el servicio de reconocimiento: {error}")
            return ""

    # ==========================================
    def hablar(self, texto: str):
        """Convierte texto en voz y lo reproduce por el altavoz."""
        if not texto:
            return
        self.motor_voz.say(texto)
        self.motor_voz.runAndWait()


# ==========================================
# Prueba rápida en consola
# ==========================================
if __name__ == "__main__":
    voz = ValentineVoice()
    voz.hablar("Hola, soy Valentine. Dime algo y te escucho.")

    texto_usuario = voz.escuchar()
    if texto_usuario:
        voz.hablar(f"Escuché que dijiste: {texto_usuario}")
    else:
        voz.hablar("No logré escuchar nada, ¿lo intentamos de nuevo?")
