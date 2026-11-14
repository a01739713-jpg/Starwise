"""🤖 AQUÍ VIVE LA IA DE STARWISE.

Todo lo que hace la inteligencia artificial pasa por este archivo:
  1. cliente_ia()      → la IA interpreta a Carmen, la clienta del caso.
  2. tutor_ia()        → la IA es Chispa, la guía que da pistas sin dar respuestas.
  3. diagnostico_ia()  → la IA lee las respuestas del diagnóstico y detecta el punto de partida.
  4. evaluar_ia()      → la IA evalúa la conversación y la propuesta con la rúbrica de competencias.

Si no hay API key, cada función regresa None y la app usa el "modo demo" (reglas en caso.py y
evaluacion.py), así que el prototipo funciona igual sin pagar nada.

Para activar la IA real: consigan una API key de Google Gemini (Google AI Studio) y pónganla en
.streamlit/secrets.toml como GEMINI_API_KEY. Ver README.
"""
import json
import os

import requests
import streamlit as st

URL = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"


def _config(nombre, default=None):
    try:
        if nombre in st.secrets:
            return st.secrets[nombre]
    except Exception:
        pass
    return os.environ.get(nombre, default)


def disponible():
    return bool(_config("GEMINI_API_KEY"))


def _llamar(sistema, mensajes, json_mode=False, temperatura=0.7):
    """mensajes = [{"role": "user"|"assistant", "content": str}]. Regresa texto o None si falla."""
    key = _config("GEMINI_API_KEY")
    if not key:
        return None
    modelo = _config("GEMINI_MODEL", "gemini-2.5-flash")
    contenidos = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
                  for m in mensajes]
    if not contenidos or contenidos[0]["role"] != "user":
        contenidos.insert(0, {"role": "user", "parts": [{"text": "(Inicia la sesión)"}]})
    cuerpo = {"systemInstruction": {"parts": [{"text": sistema}]}, "contents": contenidos,
              "generationConfig": {"temperature": temperatura}}
    if json_mode:
        cuerpo["generationConfig"]["responseMimeType"] = "application/json"
    try:
        r = requests.post(URL.format(modelo=modelo), params={"key": key}, json=cuerpo, timeout=45)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:  # sin internet, key inválida, límite gratuito, etc. → modo demo
        st.session_state["ia_error"] = str(e)[:200]
        return None


# 1 · 🤖 Cliente IA ---------------------------------------------------------------------------------
def cliente_ia(historial, contexto_caso, giro_ocurrido):
    sistema = f"""Eres Carmen Ruiz, directora general de Talavera Viva, un taller familiar de talavera en Puebla.
Hablas con un estudiante universitario que te va a ayudar a recuperar ventas. Reglas:
- Responde como una clienta real, en español de México, en máximo 70 palabras.
- Solo da la información que te pregunten. No ofrezcas soluciones ni le digas qué hacer.
- Si propone algo sin haber preguntado lo suficiente, dile que todavía no conoce bien tu negocio.
- Si su idea no cabe en el presupuesto o no se puede medir, cuestiónala con amabilidad.
- {"Ya ocurrió el giro: el banco recortó el presupuesto a $60,000." if giro_ocurrido else "Todavía no menciones problemas con el banco."}
Hechos del negocio (úsalos solo si te preguntan por ellos):
{contexto_caso}"""
    return _llamar(sistema, historial)


# 2 · 🤖 Chispa, tutora IA ----------------------------------------------------------------------------
def tutor_ia(fase, resumen):
    sistema = """Eres Chispa, la guía de Starwise: una chispa alegre y directa que acompaña a universitarios
en un reto de negocio. Tu método es socrático: NUNCA das la respuesta ni la solución del caso.
Das UNA pista corta (máximo 45 palabras) en forma de pregunta o de enfoque, ligada a una competencia:
preguntas poderosas, pensamiento estructurado, comunicación ejecutiva, adaptabilidad o iniciativa.
Hablas en español de México, de tú, con calidez y sin emojis."""
    return _llamar(sistema, [{"role": "user", "content": f"Fase: {fase}\nSituación: {resumen}\nDame una pista."}],
                   temperatura=0.8)


# 3 · 🤖 Diagnóstico ----------------------------------------------------------------------------------
def diagnostico_ia(respuestas):
    sistema = """Eres Chispa. Lee las respuestas de un universitario a 3 situaciones y dile, en máximo
2 oraciones y de tú, cuál es su punto fuerte y qué conviene que practique en el reto. Sin calificaciones."""
    texto = "\n".join(f"P: {p}\nR: {r}" for p, r in respuestas)
    return _llamar(sistema, [{"role": "user", "content": texto}], temperatura=0.5)


# 4 · 🤖 Evaluación con la rúbrica ------------------------------------------------------------------
def evaluar_ia(transcripcion, propuesta, defensa, metricas, competencias):
    sistema = f"""Eres evaluador de competencias de Starwise. Evalúas cómo trabajó un universitario en un caso
de negocio. NO das calificación numérica al alumno: das un nivel por competencia y evidencia textual.
Niveles: 1 Inicial, 2 En desarrollo, 3 Sólido, 4 Destacado.
Competencias: {", ".join(competencias)}.
Criterios: preguntas que revelan información clave (clientes, márgenes, meta, diferencial);
estructura (problema → propuesta → acciones con costo → medición); comunicación breve y convincente;
adaptación al recorte de presupuesto y manejo del tiempo; iniciativa (ir más allá de lo pedido,
explicar qué aportó él además de la IA).
Responde SOLO un JSON con esta forma:
{{"competencias": {{"<nombre>": {{"nivel": 1-4, "evidencia": "cita o hecho breve"}}}},
 "fortalezas": ["..."], "mejoras": ["..."], "senales_proactividad": ["..."], "siguiente_paso": "..."}}"""
    contenido = (f"CONVERSACIÓN:\n{transcripcion}\n\nPROPUESTA:\n{json.dumps(propuesta, ensure_ascii=False)}\n\n"
                 f"DEFENSA:\n{json.dumps(defensa, ensure_ascii=False)}\n\nMÉTRICAS:\n{json.dumps(metricas)}")
    texto = _llamar(sistema, [{"role": "user", "content": contenido}], json_mode=True, temperatura=0.2)
    if not texto:
        return None
    try:
        datos = json.loads(texto)
        assert all(c in datos["competencias"] for c in competencias)
        return datos
    except Exception:
        return None
