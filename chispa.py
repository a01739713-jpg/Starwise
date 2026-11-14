"""STARWISE · chispa.py

CHISPA: mascota (SVG propio, sin servicios externos) y tutor pedagógico
POR REGLAS. Esto NO es IA generativa: es un banco de más de 25 escenarios
socráticos. ia.py decide si usar Gemini o este motor.

Regla de pistas (visible en la interfaz): máximo 3 pistas por misión,
graduales: 1) pregunta orientadora, 2) dónde investigar, 3) ejemplo análogo
con cifras distintas. Explicar conceptos y «¿por dónde comienzo?» NO consumen
pistas, pero se registran como apoyo.
"""
from __future__ import annotations

import re

from datos import quitar_tildes

MAX_PISTAS_POR_MISION = 3

MISIONES = {
    "m1": "La primera junta",
    "m2": "La carpeta misteriosa",
    "m3": "El giro de la historia",
    "m4": "Propuesta al consejo",
}

# ---------------------------------------------------------------------------
# Mascota SVG
# ---------------------------------------------------------------------------
_OJOS = {
    "feliz": '<path d="M38 52 q6 -7 12 0" /><path d="M70 52 q6 -7 12 0" />',
    "pensando": '<circle cx="44" cy="52" r="4.5" fill="#13243F" stroke="none"/><path d="M70 50 h12" />',
    "sorpresa": '<circle cx="44" cy="51" r="6" fill="#13243F" stroke="none"/><circle cx="76" cy="51" r="6" fill="#13243F" stroke="none"/>',
    "logro": '<path d="M37 50 l7 6 l7 -6" /><path d="M69 50 l7 6 l7 -6" />',
    "calma": '<path d="M38 53 h12" /><path d="M70 53 h12" />',
    "alerta": '<circle cx="44" cy="51" r="5" fill="#13243F" stroke="none"/><circle cx="76" cy="51" r="5" fill="#13243F" stroke="none"/>',
}
_BOCA = {
    "feliz": '<path d="M48 68 q12 12 24 0" />',
    "pensando": '<path d="M52 70 q8 -4 16 2" />',
    "sorpresa": '<ellipse cx="60" cy="71" rx="6" ry="7" fill="#13243F" stroke="none"/>',
    "logro": '<path d="M44 66 q16 18 32 0 z" fill="#13243F"/>',
    "calma": '<path d="M52 70 q8 5 16 0" />',
    "alerta": '<path d="M50 72 h20" />',
}


def chispa_svg(estado: str = "feliz", tam: str = "100%") -> str:
    """SVG accesible de Chispa. `tam` es un ancho CSS relativo (no px fijos)."""
    estado = estado if estado in _OJOS else "feliz"
    extra = ""
    if estado == "pensando":
        extra = '<circle cx="104" cy="22" r="5" fill="#FFC800"/><circle cx="112" cy="10" r="3" fill="#FFC800"/>'
    if estado == "logro":
        extra = ('<path d="M10 20 l4 -8 l4 8 l-8 0 z" fill="#1E6BE6"/>'
                 '<path d="M104 26 l3 -6 l3 6 z" fill="#1E6BE6"/>')
    return f"""<svg class="chispa chispa-{estado}" viewBox="0 0 120 120" role="img"
 aria-label="Chispa, la mascota de STARWISE, con expresión {estado}" style="width:{tam};height:auto">
 <defs><radialGradient id="g-{estado}" cx="40%" cy="35%" r="70%">
  <stop offset="0%" stop-color="#FFE27A"/><stop offset="100%" stop-color="#FFC800"/></radialGradient></defs>
 <path d="M60 4 L74 38 L112 40 L82 64 L92 104 L60 82 L28 104 L38 64 L8 40 L46 38 Z"
  fill="url(#g-{estado})" stroke="#1550B8" stroke-width="4" stroke-linejoin="round"/>
 <circle cx="34" cy="64" r="6" fill="#FF9DB5" opacity=".55"/><circle cx="86" cy="64" r="6" fill="#FF9DB5" opacity=".55"/>
 <g fill="none" stroke="#13243F" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
  {_OJOS[estado]}{_BOCA[estado]}</g>{extra}
</svg>"""


# ---------------------------------------------------------------------------
# Banco de reglas
# ---------------------------------------------------------------------------
PISTAS = {
    "m1": [
        "Antes de proponer nada: ¿qué necesitarías saber de los clientes para entender por qué compran menos?",
        "Hay cuatro temas que cualquier analista revisaría: quiénes compran, por qué canal llegan, cuánto deja cada "
        "producto y qué espera Carmen el lunes. ¿Cuáles ya le preguntaste?",
        "Ejemplo distinto: en una heladería ficticia que vendió 15 % menos, la analista preguntó primero qué tipo de "
        "cliente dejó de ir (escuelas cercanas) y luego por qué. Así encontró que el problema era el horario, no el sabor.",
    ],
    "m2": [
        "Carmen dijo que las ventas bajaron 28 %. ¿Coincide eso con lo que suman los archivos? ¿Confías en que cada fila es única?",
        "Revisa la columna id_venta de ventas.csv: ordénala haciendo clic en el encabezado y busca si algún id aparece dos veces.",
        "Ejemplo distinto: una tienda ficticia reportó 210,000 cuando la suma limpia era 200,000; una venta de 10,000 estaba "
        "capturada dos veces. Variación = (nuevo − anterior) ÷ anterior × 100.",
    ],
    "m3": [
        "Con menos dinero no puedes hacerlo todo. ¿Qué acción ataca directamente el segmento que más cayó?",
        "Mira lo que Carmen dijo de los restaurantes y los tiempos de entrega, y compáralo con el margen de cada producto en costos.csv.",
        "Ejemplo distinto: con $40,000 un café ficticio puso $25,000 en lo que resolvía su queja principal y $15,000 en "
        "probarlo a pequeña escala, en lugar de repartir un poco en todo.",
    ],
    "m4": [
        "Si Carmen solo leyera una frase de tu propuesta, ¿qué problema y qué acción debería entender?",
        "Revisa que cada parte tenga respaldo: dos datos del caso, tres acciones dentro del presupuesto y un indicador que "
        "Carmen pueda medir en 30 días.",
        "Ejemplo distinto: «Las ventas a oficinas cayeron 20 %; propongo un menú empresarial con entrega en 24 h; "
        "en 30 días mediremos pedidos semanales de oficinas (meta: de 10 a 14)».",
    ],
}

COMIENZO = {
    "m1": "Empieza por entender a los clientes: pregúntale a Carmen quién compra y quién dejó de comprar.",
    "m2": "Abre ventas.csv, revisa los totales por trimestre y compáralos con el 28 % que dijo Carmen.",
    "m3": "Primero decide qué acción es imprescindible; después ajusta montos hasta quedar en verde.",
    "m4": "Escribe primero el diagnóstico en una frase con un dato; lo demás se construye encima.",
}

CONCEPTOS = {
    "variacion": ("variación porcentual", ["variacion", "porcentaje", "porcentual", "cambio %", "por ciento", "cuanto cambio"],
                  "La variación porcentual compara dos periodos: (valor nuevo − valor anterior) ÷ valor anterior × 100. "
                  "Si pasa de 50 a 40, la variación es −20 %."),
    "kpi": ("indicador o KPI", ["kpi", "indicador", "metrica", "medir"],
            "Un indicador (KPI) es una medida que te dice si vas bien hacia una meta. Uno bueno es concreto, medible "
            "y depende de lo que haces: «pedidos nuevos de hoteles por semana» es mejor que «que nos vaya bien»."),
    "margen": ("margen bruto", ["margen", "ganancia", "utilidad"],
               "El margen bruto es lo que queda de cada venta después del costo de producirla: (precio − costo) ÷ precio. "
               "Si vendes en 100 y te cuesta 60, el margen es 40 %."),
    "segmento": ("segmento", ["segmento", "segmentacion", "tipo de cliente"],
                 "Un segmento es un grupo de clientes con necesidades parecidas. Analizar por segmento ayuda a ver "
                 "dónde se concentra un problema en vez de mirar solo el total."),
    "anomalia": ("anomalía o duplicado", ["anomalia", "duplicado", "raro", "error en datos", "limpiar", "limpieza"],
                 "Una anomalía es un dato que no debería estar así: una fila repetida, un monto imposible o una fecha "
                 "fuera de rango. Antes de concluir, conviene revisar que cada registro sea único y razonable."),
    "presupuesto": ("presupuesto", ["presupuesto", "asignar", "repartir", "dinero"],
                    "Presupuestar es decidir a qué le pones recursos limitados. La pregunta clave no es «¿qué más puedo "
                    "hacer?» sino «¿qué es lo más importante con lo que tengo?»."),
    "supuesto": ("supuesto", ["supuesto", "asumir", "hipotesis"],
                 "Un supuesto es algo que das por cierto sin haberlo comprobado. Escribirlos ayuda a que otros vean qué "
                 "tendría que pasar para que tu plan funcione."),
    "riesgo": ("riesgo", ["riesgo", "que puede salir mal", "amenaza"],
               "Un riesgo es algo que podría impedir el resultado. Un buen plan lo nombra y dice cómo lo vigilarías."),
    "ticket": ("ticket promedio", ["ticket", "promedio por pedido", "valor por pedido"],
               "El ticket promedio es la venta total dividida entre el número de pedidos. Si vendes 10,000 en 20 pedidos, "
               "el ticket promedio es 500."),
    "controlable": ("indicador controlable", ["controlable", "depende de mi", "accionable"],
                    "Un indicador controlable mide algo en lo que tu acción influye directamente, por ejemplo «visitas "
                    "comerciales realizadas» o «tiempo de reposición», no algo que depende del clima o de la economía."),
}

INTENCIONES = [
    ("pedir_respuesta", ["dame la respuesta", "cual es la respuesta", "dime la solucion", "resuelvelo", "hazlo tu",
                         "respuesta correcta", "cual es el bueno"],
     "No te voy a dar la respuesta, pero sí te acompaño a encontrarla. Si quieres, usa «Dame una pista»."),
    ("frustracion", ["no se", "no entiendo nada", "estoy perdido", "estoy perdida", "me rindo", "es dificil", "ayuda"],
     "Es normal sentirse así al principio. Vamos por partes: ¿qué es lo último que entendiste bien?"),
    ("que_preguntar", ["que le pregunto", "que preguntar", "que le digo a carmen", "no se que preguntar"],
     "Piensa como detective: ¿quién compra, por dónde compra, cuánto gana Talavera Viva con cada producto y qué espera Carmen?"),
    ("filtrar", ["filtrar", "filtro", "como filtro", "como veo solo"],
     "En la pestaña «Datos» puedes elegir producto, segmento y canal. Los totales se recalculan con lo que filtres."),
    ("descargar", ["descargar", "bajar archivo", "exportar"],
     "Cada tabla tiene un botón de descarga en CSV y al final podrás bajar tu portafolio en HTML y JSON."),
    ("saludo", ["hola", "buenas", "que tal", "hey"],
     "¡Hola! Soy Chispa, tu tutora en este reto. Puedo darte pistas, explicarte conceptos o ayudarte a empezar."),
    ("gracias", ["gracias", "te agradezco", "genial", "super"],
     "¡Con gusto! Sigue así: cada decisión que justificas con un dato cuenta."),
    ("carmen_rol", ["quien es carmen", "carmen es real", "empresa real", "existe talavera"],
     "Carmen y Talavera Viva son personajes ficticios de práctica. Los números son sintéticos y sirven para aprender."),
    ("tiempo", ["cuanto tiempo", "cuanto falta", "me tardo"],
     "No hay prisa: el tiempo se registra, pero no se usa para calificarte."),
    ("evaluacion", ["me califican", "calificacion", "nota", "cuenta para", "me evalua"],
     "Aquí estás practicando: las pistas no restan puntos. Solo se reporta cuánto apoyo usaste. La prueba B sí es sin ayuda."),
]


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", quitar_tildes(t.lower())).strip()


def pista(mision: str, nivel: int) -> str:
    nivel = max(1, min(nivel, MAX_PISTAS_POR_MISION))
    return PISTAS.get(mision, PISTAS["m1"])[nivel - 1]


def comienzo(mision: str) -> str:
    return COMIENZO.get(mision, COMIENZO["m1"])


def explicar_concepto(texto: str) -> str | None:
    t = _norm(texto)
    for _, (_, claves, exp) in CONCEPTOS.items():
        if any(k in t for k in claves):
            return exp
    return None


def lista_conceptos() -> list[tuple[str, str]]:
    return [(k, v[0]) for k, v in CONCEPTOS.items()]


def responder_reglas(mensaje: str, mision: str) -> dict:
    """Responde un mensaje libre con reglas. Devuelve {'texto', 'intencion', 'es_pista'}."""
    t = _norm(mensaje)
    if re.search(r"\b(pista|hint|ayudita)\b", t):
        return {"texto": "", "intencion": "pista", "es_pista": True}
    if re.search(r"(por donde (empiezo|comienzo)|como empiezo|primer paso)", t):
        return {"texto": comienzo(mision), "intencion": "comienzo", "es_pista": False}
    for nombre, claves, resp in INTENCIONES:
        if any(re.search(r"\b" + re.escape(k) + r"\b", t) for k in claves):
            if nombre in ("saludo", "gracias") and len(t.split()) > 6:
                continue  # «hola, ¿qué es un KPI?» debe ir a conceptos
            return {"texto": resp, "intencion": nombre, "es_pista": False}
    exp = explicar_concepto(t)
    if exp:
        return {"texto": exp, "intencion": "concepto", "es_pista": False}
    return {"texto": "Buena pregunta. No tengo una respuesta preparada para eso; te sugiero «¿Por dónde comienzo?» o pedirme "
                     "una pista. También puedes preguntarme por conceptos como variación, margen o KPI.",
            "intencion": "no_reconocida", "es_pista": False}


def total_escenarios() -> int:
    return sum(len(v) for v in PISTAS.values()) + len(COMIENZO) + len(CONCEPTOS) + len(INTENCIONES) + 1
