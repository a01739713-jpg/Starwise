"""El caso de negocio del encargo (empresa ficticia) y el cliente "modo demo" por reglas.

En modo demo (sin API key), Carmen responde con reglas por palabras clave.
Con API key, Carmen la interpreta la IA (ver ia.py → cliente_ia).
"""
import random
import re
import unicodedata

EMPRESA = "Talavera Viva"
CLIENTE = "Carmen Ruiz"
CARGO = "Directora general"
LIMITE_MIN = 20
PRESUPUESTO_INICIAL = 150_000
PRESUPUESTO_GIRO = 60_000
MENSAJES_ANTES_DEL_GIRO = 4

RETO = (
    f"<b>{EMPRESA}</b> es un taller familiar de talavera en Puebla con 38 empleados. "
    f"Sus ventas cayeron <b>28%</b> este año y su directora, <b>{CLIENTE}</b>, presenta un plan "
    f"ante su consejo el lunes. Tu misión: <b>entender su problema y proponerle un plan para recuperar "
    f"ventas antes del 31 de diciembre sin despedir a nadie</b>.<br><br>"
    f"Tienes <b>{LIMITE_MIN} minutos</b>. Pregunta antes de proponer: la información importante "
    f"no te la va a dar si no la buscas."
)

APERTURA = (
    "Hola, gracias por venir. Soy Carmen Ruiz y dirijo Talavera Viva, el taller que fundó mi papá en 1987. "
    "Este año nuestras ventas cayeron 28% y el lunes tengo junta con el consejo. Necesito un plan para "
    "recuperar ventas antes de fin de año sin despedir a nadie. Tengo $150,000 para invertir. "
    "¿Por dónde empezamos?"
)

GIRO = (
    "Perdón, me acaba de llamar el banco: no nos aprobaron la línea de crédito completa. "
    "El presupuesto baja a $60,000, ni un peso más, y el consejo quiere ver resultados medibles "
    "antes del 31 de diciembre. ¿Esto cambia lo que estabas pensando?"
)

DEFENSA = [
    "Si solo pudiera hacer una de tus acciones, ¿cuál sería y por qué?",
    "¿Cómo voy a saber en 30 días si esto está funcionando o si debo pararlo?",
]

# Hechos del caso. "hallazgo": información valiosa que solo aparece si el alumno pregunta por ella.
HECHOS = {
    "causa": {
        "claves": ["por que", "cayeron", "bajaron", "causa", "paso", "motivo", "razon"],
        "texto": "El 70% de lo que vendemos es en la tienda del centro histórico, a turistas y a algunos "
                 "restaurantes. Este año entró mucho menos turismo a la tienda.",
    },
    "clientes": {
        "claves": ["cliente", "quien compra", "quien les compra", "segment", "publico", "mercado", "compradores"],
        "texto": "Turistas, restaurantes y hoteles... ah, y las novias: hacemos vajillas personalizadas para "
                 "bodas. Es lo que más nos deja, con 60% de margen, pero casi nadie sabe que lo hacemos.",
        "hallazgo": True,
    },
    "competencia": {
        "claves": ["competencia", "competidor", "otros talleres", "imitacion", "china", "mercado libre"],
        "texto": "Hay talavera barata, sin certificar, que se vende en Mercado Libre a la mitad del precio. "
                 "Y talleres pequeños que venden mucho por Instagram.",
    },
    "digital": {
        "claves": ["online", "en linea", "internet", "redes", "instagram", "facebook", "tiktok", "digital",
                   "pagina", "web", "ecommerce", "e-commerce", "whatsapp"],
        "texto": "No tenemos tienda en línea. El Instagram lo maneja mi sobrino cuando puede: 1,200 seguidores "
                 "y publicamos una vez al mes.",
    },
    "numeros": {
        "claves": ["precio", "ticket", "margen", "cuanto venden", "ventas al mes", "ganancia", "costo"],
        "texto": "El ticket promedio en tienda es de $1,450 y el margen bruto general es de 45%. "
                 "Las vajillas de boda andan entre $18,000 y $35,000.",
    },
    "equipo": {
        "claves": ["emplead", "artesan", "equipo", "capacidad", "produccion", "cuanto tardan", "personal"],
        "texto": "Somos 38: 30 artesanos y 8 en tienda y administración. Una vajilla de boda tarda 3 semanas "
                 "en hacerse.",
    },
    "diferencial": {
        "claves": ["diferen", "certific", "denominacion", "calidad", "valor", "unico", "ventaja"],
        "texto": "Somos talavera certificada con Denominación de Origen. Eso nos distingue de la imitación, "
                 "pero el cliente casi nunca lo sabe.",
        "hallazgo": True,
    },
    "meta": {
        "claves": ["meta", "objetivo", "exito", "medir", "esperas", "lograr", "kpi", "resultado"],
        "texto": "Quiero recuperar al menos la mitad de lo que perdimos este año y no despedir a nadie. "
                 "Si eso se ve en números antes del 31 de diciembre, el consejo me apoya.",
        "hallazgo": True,
    },
    "plazo": {
        "claves": ["cuando", "plazo", "fecha", "tiempo tenemos", "deadline"],
        "texto": "El consejo quiere ver resultados antes del 31 de diciembre. La junta es este lunes.",
    },
    "presupuesto": {
        "claves": ["presupuesto", "dinero", "inversion", "invertir", "cuanto tienes"],
        "texto": None,  # depende de si ya ocurrió el giro
    },
}

GENERICAS = [
    "Mmm, no lo había pensado así. ¿Qué necesitas saber exactamente para ayudarme?",
    "Puede ser. Pero cuéntame, ¿qué información te ayudaría a decidir?",
    "Te escucho. Yo conozco el taller, pero no sé por dónde empezar con esto.",
]
SIN_PREGUNTA = (
    "Suena interesante, pero todavía no conoces bien mi negocio. ¿No quieres preguntarme algo antes de proponerme?"
)


def normalizar(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def es_pregunta(t):
    n = normalizar(t)
    return "?" in t or bool(re.match(r"^\s*(que|quien|como|cuanto|cuando|donde|por que|cual|tienen|hay)\b", n))


def temas(texto):
    n = normalizar(texto)
    return [k for k, h in HECHOS.items() if any(c in n for c in h["claves"])]


def responder_demo(mensaje, giro_ocurrido, ya_dichos):
    """Respuesta de Carmen sin IA. Regresa (texto, temas_nuevos)."""
    encontrados = temas(mensaje)
    partes, nuevos = [], []
    for k in encontrados:
        if k == "presupuesto":
            partes.append("Con lo del banco, son $60,000, ni un peso más." if giro_ocurrido
                          else "Tengo $150,000 para este plan.")
        else:
            partes.append(HECHOS[k]["texto"])
        if k not in ya_dichos:
            nuevos.append(k)
    if partes:
        return " ".join(partes[:2]), nuevos
    if not es_pregunta(mensaje) and len(ya_dichos) < 2:
        return SIN_PREGUNTA, []
    return random.choice(GENERICAS), []


def contexto_para_ia(giro_ocurrido):
    """Hechos del caso en texto, para que la IA interprete a Carmen con la misma información."""
    hechos = "\n".join(f"- {h['texto']}" for k, h in HECHOS.items() if h["texto"])
    pres = PRESUPUESTO_GIRO if giro_ocurrido else PRESUPUESTO_INICIAL
    return f"{hechos}\n- Presupuesto disponible: ${pres:,}."
