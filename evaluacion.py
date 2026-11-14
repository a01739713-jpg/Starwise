"""Rúbrica de competencias y evaluación por reglas (modo demo, sin IA).

Las 5 competencias salen de las validaciones del equipo:
- Erik (CVDP, Tec Puebla): pensamiento estructurado bajo presión, comunicación ejecutiva,
  autogestión y adaptabilidad (colaboración e influencia queda para retos en equipo, fase 1).
- Panel EdTech y mentora: calidad de las preguntas (preguntas poderosas).
- CVDP: iniciativa/proactividad (el 20% que brilla).
"""
import re

from caso import HECHOS, es_pregunta, normalizar

COMPETENCIAS = [
    "Preguntas poderosas",
    "Pensamiento estructurado bajo presión",
    "Comunicación ejecutiva",
    "Autogestión y adaptabilidad",
    "Iniciativa",
]
NIVELES = {1: "Inicial", 2: "En desarrollo", 3: "Sólido", 4: "Destacado"}

RUBRICA = {
    "Preguntas poderosas": "Pregunta antes de proponer y descubre información clave (clientes, margen, meta, diferencial).",
    "Pensamiento estructurado bajo presión": "Ordena problema → propuesta → acciones con costo → medición, dentro del tiempo.",
    "Comunicación ejecutiva": "Explica su idea en pocas palabras y responde la defensa directo, con un porqué.",
    "Autogestión y adaptabilidad": "Ajusta su plan al recorte de presupuesto y administra tiempo y pistas.",
    "Iniciativa": "Va más allá de lo pedido y deja claro qué aportó él, además de la IA.",
}


def _palabras(t):
    return len(re.findall(r"\w+", t or ""))


def _nivel(puntos, cortes):
    """cortes = (para 2, para 3, para 4)"""
    return 1 + sum(puntos >= c for c in cortes)


def evaluar_demo(s):
    """`s` = dict con: mensajes_usuario, temas, propuesta, defensa, minutos, pistas, giro_antes_de_propuesta."""
    msgs = s["mensajes_usuario"]
    preguntas = [m for m in msgs if es_pregunta(m)]
    temas = set(s["temas"])
    hallazgos = [k for k in temas if HECHOS[k].get("hallazgo")]
    p, d = s["propuesta"], s["defensa"]
    comp, fortalezas, mejoras, senales = {}, [], [], []

    # 1 · Preguntas poderosas
    pts = len(temas) + len(hallazgos)
    n = _nivel(pts, (2, 4, 6))
    mejor = max(preguntas, key=len) if preguntas else ""
    comp["Preguntas poderosas"] = {"nivel": n, "evidencia": f"Hiciste {len(preguntas)} preguntas y descubriste "
                                   f"{len(temas)} temas del negocio." + (f' Tu mejor pregunta: "{mejor[:90]}"' if mejor else "")}
    if "clientes" in temas:
        fortalezas.append("Preguntaste por los clientes y encontraste las vajillas de boda, el producto con más margen.")
    else:
        mejoras.append("No preguntaste quién compra. Ahí estaba el hallazgo clave: las vajillas de boda dejan 60% de margen.")

    # 2 · Pensamiento estructurado
    campos = [p.get("problema"), p.get("propuesta"), p.get("acciones"), p.get("medicion")]
    llenos = sum(_palabras(c) >= 5 for c in campos)
    acciones = [l for l in (p.get("acciones") or "").splitlines() if _palabras(l) >= 3]
    con_numeros = bool(re.search(r"\d", p.get("acciones", "") + p.get("medicion", "")))
    pts = llenos + min(len(acciones), 3) + con_numeros + (s["minutos"] <= 20)
    comp["Pensamiento estructurado bajo presión"] = {
        "nivel": _nivel(pts, (3, 6, 8)),
        "evidencia": f"Completaste {llenos} de 4 partes, con {len(acciones)} acciones"
                     + (" con cifras" if con_numeros else " sin cifras") + f", en {s['minutos']:.0f} minutos."}
    if not con_numeros:
        mejoras.append("Ponle números a tus acciones y a tu medición: costo, meta y plazo.")

    # 3 · Comunicación ejecutiva
    w_prop = _palabras(p.get("propuesta"))
    d_resp = [r for r in d if r]
    directas = sum(10 <= _palabras(r) <= 90 for r in d_resp)
    con_porque = sum("porque" in normalizar(r) or "ya que" in normalizar(r) for r in d_resp)
    pts = (5 <= w_prop <= 30) * 2 + directas + con_porque
    comp["Comunicación ejecutiva"] = {"nivel": _nivel(pts, (2, 4, 5)),
                                      "evidencia": f"Tu propuesta en una frase tiene {w_prop} palabras; "
                                                   f"{con_porque} de 2 respuestas de defensa dan un porqué."}
    if w_prop > 30:
        mejoras.append("Tu propuesta en una frase fue larga: intenta decirla en menos de 25 palabras.")
    elif 5 <= w_prop <= 30:
        fortalezas.append("Resumiste tu propuesta de forma breve, como se presenta a un consejo.")

    # 4 · Autogestión y adaptabilidad
    todo = normalizar(" ".join(str(v) for v in p.values()))
    ajusto = bool(re.search(r"60[\s,.]?000|60 ?mil|\$ ?60", todo)) or "recorte" in todo or "presupuesto" in todo
    pts = ajusto * 3 + (s["minutos"] <= 20) + (s["pistas"] <= 2)
    comp["Autogestión y adaptabilidad"] = {"nivel": _nivel(pts, (1, 3, 5)),
                                           "evidencia": ("Ajustaste tu plan al nuevo presupuesto de $60,000. " if ajusto
                                                         else "Tu plan no menciona el recorte a $60,000. ")
                                                        + f"Usaste {s['pistas']} pistas."}
    if ajusto:
        fortalezas.append("Te adaptaste al giro: tu plan considera el recorte de presupuesto.")
        senales.append("Ajustaste el plan después del giro sin que nadie te lo pidiera.")
    else:
        mejoras.append("Cuando cambia el escenario, di explícitamente qué cambias de tu plan y por qué.")

    # 5 · Iniciativa
    uso_ia = p.get("aporte", "")
    pts = len(hallazgos) + (_palabras(uso_ia) >= 12) + ("meta" in temas) + (len(acciones) > 3)
    comp["Iniciativa"] = {"nivel": _nivel(pts, (1, 2, 4)),
                          "evidencia": f"Descubriste {len(hallazgos)} de 3 hallazgos ocultos"
                                       + ("; explicaste qué aportaste tú además de la IA." if _palabras(uso_ia) >= 12
                                          else "; no explicaste qué aportaste tú además de la IA.")}
    if "meta" in temas:
        senales.append("Preguntaste cuál era la meta antes de proponer: así empiezan los consultores.")
    if "diferencial" in temas:
        senales.append("Indagaste qué hace única a la empresa (Denominación de Origen).")
    if _palabras(uso_ia) >= 12:
        senales.append("Dejaste claro qué agregaste tú a lo que te dio la IA.")
    if not senales:
        senales.append("Todavía no aparecen señales de proactividad: la próxima vez ve un paso más allá de lo que te piden.")

    debil = min(comp, key=lambda k: comp[k]["nivel"])
    return {"competencias": comp, "fortalezas": fortalezas[:3] or ["Terminaste el reto completo y defendiste tu propuesta."],
            "mejoras": mejoras[:3], "senales_proactividad": senales,
            "siguiente_paso": f"En tu próximo encargo enfócate en: {debil.lower()}. {RUBRICA[debil]}"}
