# ============================================================
# Project Valentine - Vision v1.0
# Captura de pantalla y webcam, analizadas con Gemini Vision
# ============================================================

import io
from google import genai
from PIL import ImageGrab, Image

# Requiere: pip install pillow mss opencv-python google-genai
# - pillow / mss -> captura de pantalla
# - opencv-python -> captura de webcam

client = genai.Client()
MODELO_VISION = "gemini-2.5-flash"  # Soporta texto + imagen en la misma llamada


class ValentineVision:
    """
    Captura lo que el usuario ve (pantalla) o lo que la webcam ve,
    y le pregunta a Gemini qué está pasando ahí (bug de código,
    partida de Minecraft, etc.). Devuelve solo texto: la descripción.
    """

    def capturar_pantalla(self) -> Image.Image:
        """Toma una captura de la pantalla completa."""
        return ImageGrab.grab()

    def capturar_webcam(self):
        """
        Toma una foto desde la webcam usando OpenCV.
        Devuelve una imagen PIL, o None si no se pudo acceder a la cámara.
        """
        import cv2  # import local: evita que el módulo entero falle si no hay cv2 instalado

        camara = cv2.VideoCapture(0)
        ok, frame = camara.read()
        camara.release()

        if not ok:
            print("[Vision] No se pudo acceder a la webcam.")
            return None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)

    # ==========================================
    def analizar_imagen(self, imagen: Image.Image, pregunta: str = None) -> str:
        """
        Envía una imagen (pantalla o webcam) a Gemini Vision junto con
        una pregunta. Si no se da pregunta, usa una genérica de soporte.
        """
        if imagen is None:
            return "No tengo ninguna imagen para revisar ahora mismo."

        pregunta_final = pregunta or (
            "Describe brevemente qué está pasando en esta imagen. "
            "Si ves código con errores, señala cuál podría ser el problema. "
            "Si es un juego, di qué está ocurriendo. Responde en español, breve."
        )

        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")
        bytes_imagen = buffer.getvalue()

        try:
            respuesta = client.models.generate_content(
                model=MODELO_VISION,
                contents=[
                    {"mime_type": "image/png", "data": bytes_imagen},
                    pregunta_final
                ]
            )
            return respuesta.text.strip()

        except Exception as error:
            print(f"[Vision] Error analizando imagen: {error}")
            return "Tuve un problema mirando la pantalla, ¿lo intentamos de nuevo?"

    # ==========================================
    def revisar_pantalla(self, pregunta: str = None) -> str:
        """Atajo: captura pantalla + analiza, en un solo paso."""
        imagen = self.capturar_pantalla()
        return self.analizar_imagen(imagen, pregunta)

    def revisar_webcam(self, pregunta: str = None) -> str:
        """Atajo: captura webcam + analiza, en un solo paso."""
        imagen = self.capturar_webcam()
        return self.analizar_imagen(imagen, pregunta)


# ==========================================
# Prueba rápida en consola
# ==========================================
if __name__ == "__main__":
    vision = ValentineVision()
    print("[Vision] Capturando pantalla y analizando con Gemini...")
    descripcion = vision.revisar_pantalla()
    print(f"\nValentine ve: {descripcion}")
