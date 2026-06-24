# ============================================================
# Project Valentine - Avatar Bridge v1.0
# Une Memory + Brain + Vision + Voice, y expone la emoción
# actual para que el motor del avatar (Unity, Live2D, etc.)
# sepa qué expresión/animación mostrar.
# ============================================================

import json
import os
import time
from valentine_brain import ValentineBrain
from valentine_vision import ValentineVision
from valentine_voice import ValentineVoice

# Archivo "puente": el motor del avatar (sea Unity, Godot, Live2D, lo que sea)
# lee este JSON para saber qué emoción mostrar AHORA MISMO.
# Es la forma más simple de conectar Python <-> un motor gráfico externo,
# sin necesitar sockets ni una API local todavía.
ARCHIVO_ESTADO_AVATAR = "avatar_estado.json"


class ValentineAvatarBridge:
    """
    Orquesta una interacción completa:
    1. Escucha al usuario (voz) o recibe texto directo.
    2. Opcionalmente revisa la pantalla/webcam si el usuario lo pide.
    3. Procesa todo con el Brain (memoria + Gemini).
    4. Habla la respuesta.
    5. Escribe la emoción resultante en un archivo que el avatar puede leer.
    """

    def __init__(self, usar_voz: bool = True):
        self.brain = ValentineBrain()
        self.vision = ValentineVision()
        self.usar_voz = usar_voz
        self.voice = ValentineVoice() if usar_voz else None

    # ==========================================
    def _publicar_estado_para_avatar(self, emocion: str, hablando: bool):
        """
        Escribe el estado actual en un JSON pequeño y simple.
        El motor del avatar (en C#, GDScript, JS, lo que sea) solo
        necesita leer este archivo cada X milisegundos para reaccionar.
        """
        estado = {
            "emocion": emocion,
            "hablando": hablando,
            "timestamp": time.time()
        }
        with open(ARCHIVO_ESTADO_AVATAR, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False)

    # ==========================================
    def procesar_mensaje_texto(self, texto_usuario: str) -> str:
        """Flujo simple: el usuario escribe texto (sin voz ni visión)."""
        respuesta, emocion = self.brain.procesar_entrada(texto_usuario)
        self._publicar_estado_para_avatar(emocion, hablando=True)

        if self.usar_voz:
            self.voice.hablar(respuesta)

        self._publicar_estado_para_avatar(emocion, hablando=False)
        return respuesta

    # ==========================================
    def procesar_con_pantalla(self, pregunta_usuario: str = None) -> str:
        """
        Flujo con visión: revisa la pantalla, describe lo que ve,
        y lo pasa como contexto extra al Brain para que responda
        con eso en mente (ej: "tengo un error en mi código").
        """
        descripcion_pantalla = self.vision.revisar_pantalla()
        mensaje_compuesto = (
            f"{pregunta_usuario or 'Mira mi pantalla y ayúdame'} "
            f"[Lo que Valentine ve en la pantalla: {descripcion_pantalla}]"
        )
        return self.procesar_mensaje_texto(mensaje_compuesto)

    # ==========================================
    def ciclo_por_voz(self):
        """
        Flujo completo por voz: escucha al usuario, procesa, y responde
        hablando. Pensado para correr en un loop continuo.
        """
        if not self.usar_voz:
            print("[Bridge] La voz está desactivada en esta instancia.")
            return

        texto_usuario = self.voice.escuchar()
        if not texto_usuario:
            return

        self.procesar_mensaje_texto(texto_usuario)

    # ==========================================
    def loop_continuo(self):
        """Mantiene a Valentine escuchando indefinidamente. Ctrl+C para salir."""
        print("[Bridge] Valentine está activa y escuchando. Ctrl+C para detener.")
        try:
            while True:
                self.ciclo_por_voz()
        except KeyboardInterrupt:
            print("\n[Bridge] Valentine se despide por ahora.")


# ==========================================
# Prueba rápida en consola (modo texto, sin voz, para probar rápido)
# ==========================================
if __name__ == "__main__":
    bridge = ValentineAvatarBridge(usar_voz=False)

    print("Valentine está despierta (modo texto). Escribe 'salir' para terminar.")
    print("Escribe 'mira mi pantalla' para probar el módulo de visión.\n")

    while True:
        entrada = input("Tú: ")
        if entrada.lower() in ("salir", "exit", "quit"):
            print("Valentine: ¡Nos vemos pronto!")
            break

        if "pantalla" in entrada.lower():
            respuesta = bridge.procesar_con_pantalla(entrada)
        else:
            respuesta = bridge.procesar_mensaje_texto(entrada)

        print(f"Valentine: {respuesta}")
        print(f"(revisa el archivo {ARCHIVO_ESTADO_AVATAR} para ver la emoción)\n")
