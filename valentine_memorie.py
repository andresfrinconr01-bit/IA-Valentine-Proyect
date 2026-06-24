# ============================================================
# Project Valentine - Memory System v3.0
# Memoria persistente en disco + recapitulación de contexto
# ============================================================

import json
import os
from datetime import datetime


class ValentineMemory:
    """
    Sistema de memoria persistente para Valentine.

    Responsabilidades:
    - Guardar y cargar datos del usuario desde un archivo .json en disco.
    - Registrar el historial de conversación (corto y largo plazo).
    - Detectar y guardar "recuerdos importantes" (frases clave del usuario).
    - Generar un bloque de texto ("contexto") que se inyecta en el prompt
      enviado a la API de Gemini, para que la IA recuerde quién es el
      usuario y qué ha pasado antes.

    Esta clase NO llama a Gemini directamente. Solo prepara la memoria.
    La conexión real con la API vive en otro archivo (ver valentine_brain.py).
    """

    def __init__(self, archivo_recuerdos="valentine_diario.json",
                 limite_corto_plazo=15, limite_largo_plazo=1000):
        self.archivo_recuerdos = archivo_recuerdos
        self.limite_corto_plazo = limite_corto_plazo
        self.limite_largo_plazo = limite_largo_plazo

        self.datos = self._estructura_base()
        self.cargar_de_disco()

        if not self.datos["usuario_principal"]:
            self.inicializar_usuario("Andrés")

    # ==========================================
    # ESTRUCTURA BASE
    # ==========================================
    def _estructura_base(self):
        return {
            "usuario_principal": None,
            "datos_clave": {
                "gustos": [],
                "detalles_aprendidos": {},
                "personalidad_preferida": "cariñosa_y_juguetona"
            },
            "recuerdos_importantes": [],
            "historial_conversacion": [],
            "ultima_actualizacion": None
        }

    def _validar_estructura(self, datos):
        campos = [
            "usuario_principal", "datos_clave",
            "recuerdos_importantes", "historial_conversacion"
        ]
        return all(campo in datos for campo in campos)

    # ==========================================
    # CARGA Y GUARDADO EN DISCO
    # ==========================================
    def cargar_de_disco(self):
        """Carga la memoria desde el archivo JSON. Si no existe, crea uno nuevo."""
        if not os.path.exists(self.archivo_recuerdos):
            print(f"[Memory] Creando nuevo diario: {self.archivo_recuerdos}")
            self.guardar_en_disco()
            return

        try:
            with open(self.archivo_recuerdos, "r", encoding="utf-8") as f:
                datos = json.load(f)

            if not self._validar_estructura(datos):
                raise ValueError("Estructura de memoria inválida o incompleta")

            self.datos = datos
            print("[Memory] Recuerdos cargados correctamente.")

        except (json.JSONDecodeError, ValueError, OSError) as error:
            print(f"[Memory] No se pudo cargar el diario ({error}). Empezando uno nuevo.")
            self.datos = self._estructura_base()
            self.guardar_en_disco()

    def guardar_en_disco(self):
        """Guarda el estado actual de la memoria en el archivo JSON."""
        self.datos["ultima_actualizacion"] = datetime.now().isoformat()
        try:
            with open(self.archivo_recuerdos, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, ensure_ascii=False, indent=2)
        except OSError as error:
            print(f"[Memory] Error guardando en disco: {error}")

    # ==========================================
    # USUARIO Y GUSTOS
    # ==========================================
    def inicializar_usuario(self, nombre):
        self.datos["usuario_principal"] = nombre
        self.agregar_gusto("Minecraft")
        self.agregar_gusto("programación")
        self.guardar_en_disco()
        print(f"[Memory] Usuario principal: {nombre}")

    def agregar_gusto(self, gusto):
        gustos = self.datos["datos_clave"]["gustos"]
        if gusto not in gustos:
            gustos.append(gusto)
            self.guardar_en_disco()

    def aprender_detalle(self, clave, valor):
        """Guarda un dato suelto sobre el usuario, ej: aprender_detalle('juego_favorito', 'Minecraft')."""
        self.datos["datos_clave"]["detalles_aprendidos"][clave] = valor
        self.guardar_en_disco()

    # ==========================================
    # HISTORIAL DE CONVERSACIÓN
    # ==========================================
    def agregar_mensaje(self, rol, contenido):
        """
        Registra un mensaje en el historial.
        rol: 'usuario' o 'valentine'
        """
        entrada = {
            "rol": rol,
            "contenido": contenido,
            "timestamp": datetime.now().isoformat()
        }
        self.datos["historial_conversacion"].append(entrada)

        # Recorta el historial si supera el límite de largo plazo
        if len(self.datos["historial_conversacion"]) > self.limite_largo_plazo:
            self.datos["historial_conversacion"].pop(0)

        self._detectar_recuerdo_importante(rol, contenido)
        self.guardar_en_disco()

    def _detectar_recuerdo_importante(self, rol, contenido):
        """
        Detección simple de frases que vale la pena recordar a largo plazo.
        Busca palabras clave típicas de información personal relevante.
        """
        if rol != "usuario":
            return

        gatillos = ["me llamo", "mi cumpleaños", "me gusta", "odio",
                    "tengo miedo", "mi sueño", "siempre quise", "recuerda que"]

        texto = contenido.lower()
        if any(gatillo in texto for gatillo in gatillos):
            self.agregar_recuerdo_importante(contenido)

    def agregar_recuerdo_importante(self, contenido):
        recuerdo = {
            "contenido": contenido,
            "timestamp": datetime.now().isoformat()
        }
        self.datos["recuerdos_importantes"].append(recuerdo)
        # Mantenemos solo los 50 recuerdos importantes más recientes
        self.datos["recuerdos_importantes"] = self.datos["recuerdos_importantes"][-50:]
        self.guardar_en_disco()
        print(f"[Memory] Nuevo recuerdo importante guardado: \"{contenido[:50]}...\"")

    # ==========================================
    # RECAPITULACIÓN / CONTEXTO PARA GEMINI
    # ==========================================
    def recapitular(self, cantidad_mensajes=None):
        """
        Devuelve un resumen legible de la sesión actual:
        usuario, gustos, recuerdos clave e historial reciente.
        Esto es lo que se inyecta en el prompt antes de llamar a Gemini.
        """
        limite = cantidad_mensajes or self.limite_corto_plazo
        historial_reciente = self.datos["historial_conversacion"][-limite:]
        recuerdos = self.datos["recuerdos_importantes"][-5:]

        bloques = [
            f"Usuario: {self.datos['usuario_principal']}",
            f"Gustos conocidos: {', '.join(self.datos['datos_clave']['gustos']) or 'ninguno aún'}",
        ]

        detalles = self.datos["datos_clave"]["detalles_aprendidos"]
        if detalles:
            detalles_txt = ", ".join(f"{k}: {v}" for k, v in detalles.items())
            bloques.append(f"Detalles aprendidos: {detalles_txt}")

        if recuerdos:
            bloques.append("Recuerdos importantes:")
            bloques.extend(f"- {r['contenido']}" for r in recuerdos)

        if historial_reciente:
            bloques.append("Historial reciente de la conversación:")
            bloques.extend(f"{m['rol']}: {m['contenido']}" for m in historial_reciente)

        return "\n".join(bloques)

    def obtener_contexto_para_gemini(self):
        """Alias explícito: el texto que se concatena al prompt enviado a Gemini."""
        return self.recapitular()


# ==========================================
# Prueba rápida (solo corre si ejecutas este archivo directamente)
# ==========================================
if __name__ == "__main__":
    memoria = ValentineMemory()
    memoria.agregar_mensaje("usuario", "Hola Valentine, me llamo Andrés y me gusta el café")
    memoria.agregar_mensaje("valentine", "Hola Andrés! Que bueno saber eso")

    print("\n--- CONTEXTO PARA GEMINI ---")
    print(memoria.obtener_contexto_para_gemini())

