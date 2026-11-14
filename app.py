"""Starwise · prototipo del hackathon Talavera Valley 2026 (Track 03 EdTech) · equipo Data Spark.

Correr:  streamlit run app.py
La IA está en ia.py (marcada con 🤖 en este archivo). Sin API key funciona en "modo demo".
"""
import datetime as dt
import html
import time
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import caso
import chispa
import datos
import ia
from evaluacion import COMPETENCIAS, NIVELES, RUBRICA, evaluar_demo

BASE = Path(__file__).parent
EVIDENCIA = BASE / "evidencia" / "sesiones.csv"

st.set_page_config(page_title="Starwise", page_icon=str(BASE / "assets" / "chispa_icon.png"), layout="centered")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');
/* Estilo inspirado en apps de aprendizaje: tipografía redonda, botones "3D", tarjetas con borde grueso.
   Paleta: azul Tec claro #1E6BE6 (sombra #1550B8) + dorado de Chispa #FFC800. */
html, body, [class*="css"], .stMarkdown, .stTextInput, .stTextArea, .stSelectbox, button, input, textarea{
  font-family:'Nunito', Arial, sans-serif !important;}
.block-container{max-width:860px;padding-top:2rem}
h1,h2,h3,h4{font-family:'Nunito', Arial, sans-serif !important;font-weight:900 !important;color:#13243F}
.pb-titulo{font-size:2.6rem;font-weight:900;color:#1E6BE6;margin:0;animation:pb-entra .6s ease-out both}
.pb-sub{color:#4B5A72;font-size:1.15rem;font-weight:700;margin-top:.2rem;animation:pb-entra .6s .1s ease-out both}

/* Botones 3D */
.stButton>button, .stFormSubmitButton>button, .stDownloadButton>button{
  border-radius:16px !important;border:2px solid #DDE5F2 !important;background:#FFFFFF !important;color:#1E6BE6 !important;
  font-weight:900 !important;text-transform:uppercase;letter-spacing:.06em;padding:.65rem 1.3rem !important;
  box-shadow:0 4px 0 #DDE5F2 !important;transition:transform .08s, box-shadow .08s, filter .15s}
.stButton>button[kind="primary"], .stFormSubmitButton>button[kind="primary"], .stDownloadButton>button[kind="primary"],
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"]{
  background:#1E6BE6 !important;color:#FFFFFF !important;border-color:#1550B8 !important;box-shadow:0 5px 0 #1550B8 !important}
.stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover{filter:brightness(1.06)}
.stButton>button:active, .stFormSubmitButton>button:active, .stDownloadButton>button:active{transform:translateY(4px);box-shadow:none !important}
.stButton>button:disabled{opacity:.5}

/* Campos y tarjetas */
.stTextInput input, .stTextArea textarea, [data-baseweb="select"]>div{border-radius:14px !important;border:2px solid #DDE5F2 !important;background:#FFFFFF !important}
.stTextInput input:focus, .stTextArea textarea:focus{border-color:#1E6BE6 !important}
[data-testid="stForm"]{border:2px solid #DDE5F2;border-radius:20px;box-shadow:0 5px 0 #DDE5F2;background:#FFFFFF;animation:pb-pop .5s ease-out both}
.pb-dato{background:#FFFFFF;border:2px solid #DDE5F2;border-radius:18px;padding:14px 16px;margin-bottom:12px;
  box-shadow:0 5px 0 #DDE5F2;animation:pb-pop .55s ease-out both}
.pb-dato:nth-child(2){animation-delay:.1s}
.pb-dato .v{font-size:1.7rem;font-weight:900;color:#1E6BE6}
.pb-dato .f{font-size:.78rem;color:#4B5A72;font-weight:600}
.pb-cliente{background:#EAF2FF;border:2px solid #B9D3FF;border-radius:16px;padding:12px 16px;margin:6px 0;font-weight:700}
[data-testid="stMetric"]{background:#FFFFFF;border:2px solid #DDE5F2;border-radius:18px;padding:10px 14px;box-shadow:0 4px 0 #DDE5F2;animation:pb-pop .5s ease-out both}
[data-testid="stMetricValue"]{color:#1E6BE6;font-weight:900}
[data-testid="stChatMessage"]{border-radius:18px;border:2px solid #DDE5F2;background:#FFFFFF;animation:pb-mensaje .35s ease-out both}
[data-testid="stProgress"] div[role="progressbar"]>div>div{border-radius:999px}
[data-testid="stSidebar"]{background:#EAF2FF}

/* Animaciones */
@keyframes pb-pop{0%{opacity:0;transform:translateY(16px) scale(.96)}65%{opacity:1;transform:translateY(-3px) scale(1.01)}100%{transform:none}}
@keyframes pb-entra{from{opacity:0;transform:translateX(-18px)}to{opacity:1;transform:none}}
@keyframes pb-mensaje{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion: reduce){*{animation:none !important;transition:none !important}}
</style>""", unsafe_allow_html=True)

DF = datos.cargar()

# ---------------------------------------------------------------- estado de la sesión
DEFAULTS = dict(paso=0, perfil={}, diag={}, diag_lectura="", chat=[], temas=[], giro=False, fase="conversacion",
                inicio=None, fin=None, pistas=0, ultima_pista="", propuesta={}, defensa=["", ""],
                resultado=None, modo="", guardado=False, racha=0, celebrado=False)
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)
S = st.session_state


def chispa_dice(texto, estado="guia", tam=100):
    st.markdown(chispa.burbuja(texto, estado, tam), unsafe_allow_html=True)


def ir(paso):
    S.paso = paso
    st.rerun()


def minutos():
    if not S.inicio:
        return 0.0
    return ((S.fin or time.time()) - S.inicio) / 60


# ---------------------------------------------------------------- barra lateral
with st.sidebar:
    st.markdown(chispa.sola("logro" if S.paso == 3 else "guia", 90), unsafe_allow_html=True)
    st.markdown(f"**Tu racha:** {S.racha} reto(s) completado(s)")
    pasos = ["Perfil", "Diagnóstico", "Reto", "Resultados"]
    st.progress(min(S.paso, 3) / 3, text=f"Paso {min(S.paso, 3) + 1} de 4 · {pasos[min(S.paso, 3)]}")
    st.caption("🤖 IA activa (Gemini)" if ia.disponible() else "Modo demo: sin API key, la clienta y la evaluación usan reglas.")
    if S.get("ia_error"):
        st.caption(f"La IA no respondió y se usó el modo demo. Detalle: {S.ia_error}")
    st.divider()
    if st.checkbox("Panel del equipo (evidencia)"):
        if EVIDENCIA.exists():
            ev = pd.read_csv(EVIDENCIA)
            st.write(f"{len(ev)} sesiones registradas")
            st.dataframe(ev, width="stretch", height=220)
            st.download_button("Descargar evidencia (CSV)", ev.to_csv(index=False).encode("utf-8"),
                               "evidencia_starwise.csv", "text/csv")
        else:
            st.write("Todavía no hay sesiones guardadas.")
    if st.button("Reiniciar sesión"):
        racha = S.racha
        for k, v in DEFAULTS.items():
            S[k] = v if not isinstance(v, (list, dict)) else type(v)()
        S.defensa, S.racha = ["", ""], racha
        st.rerun()

# Barra de avance arriba, estilo app de aprendizaje
st.progress(min(S.paso, 3) / 3)

# ================================================================ PASO 0 · PERFIL
if S.paso == 0:
    st.markdown('<p class="pb-titulo">Starwise</p><p class="pb-sub">Experiencia práctica documentada '
                'antes de tu primer empleo.</p>', unsafe_allow_html=True)
    chispa_dice("¡Hola! Soy <b>Chispa</b>. Te voy a poner frente a un problema real de una empresa y te voy a "
                "acompañar mientras lo resuelves. Aquí no hay calificaciones: hay <b>retroalimentación</b> "
                "y un <b>portafolio</b> que puedes poner en tu CV. Primero, cuéntame de ti.")
    with st.form("f_perfil"):
        nombre = st.text_input("¿Cómo te llamas? (puedes poner solo tus iniciales)")
        c1, c2 = st.columns(2)
        carrera = c1.selectbox("¿Qué estudias?", list(datos.CARRERAS))
        semestre = c2.selectbox("Semestre", list(range(1, 11)), index=4)
        intereses = st.multiselect("¿Qué te interesa además de tu carrera?",
                                   ["Emprender", "Vender y negociar", "Marketing digital", "Analizar datos",
                                    "Comunicar y presentar", "Liderar equipos"])
        antes = st.slider("Del 1 al 5, ¿qué tan listo te sientes hoy para una entrevista o un primer proyecto?", 1, 5, 3)
        mayor = st.checkbox("Tengo 18 años o más, o cuento con autorización de mi madre, padre o tutor para usar Starwise.")
        if st.form_submit_button("Empezar", type="primary"):
            if not mayor:
                st.error("Para continuar necesitamos confirmar tu edad o la autorización de tu tutor.")
            else:
                S.perfil = dict(nombre=nombre.strip() or "Participante", carrera=carrera, semestre=semestre,
                                intereses=intereses, antes=antes)
                ir(1)

# ================================================================ PASO 1 · DIAGNÓSTICO
elif S.paso == 1:
    p = S.perfil
    st.subheader(f"Diagnóstico de {p['nombre']}")
    chispa_dice(f"Antes del reto, mira lo que dicen los datos sobre tu camino en <b>{html.escape(p['carrera'])}</b>. "
                "No es para asustarte: es para que sepas por qué practicar desde ya vale la pena.")
    tarjetas = datos.tarjeta_carrera(DF, p["carrera"])          # dato real del Repositorio EdTech
    cols = st.columns(2)
    for i, (etiqueta, d) in enumerate(tarjetas):
        enlace = f' · <a href="{d["enlace"]}" target="_blank">ver fuente</a>' if d["enlace"] else ""
        cols[i % 2].markdown(f'<div class="pb-dato"><div>{etiqueta}</div><div class="v">{d["valor"]}</div>'
                             f'<div class="f">{html.escape(str(d["fuente"]))}{enlace}</div></div>',
                             unsafe_allow_html=True)
    st.caption("Datos del Repositorio EdTech del hackathon (IMCO, UVM, INEGI).")

    st.markdown("#### Tres situaciones rápidas")
    preguntas = ["Un cliente te dice: \"quiero vender más\". ¿Qué le preguntarías primero?",
                 "Tienes 10 minutos para preparar una presentación y te cambian el tema. ¿Qué haces?",
                 "En una frase: ¿por qué alguien debería contratarte?"]
    with st.form("f_diag"):
        resp = [st.text_area(q, key=f"d{i}", height=80) for i, q in enumerate(preguntas)]
        listo = st.form_submit_button("Ver mi punto de partida", type="primary")
    if listo:
        if not all(r.strip() for r in resp):
            st.warning("Responde las tres situaciones; no hay respuestas correctas.")
        else:
            S.diag = dict(zip(preguntas, resp))
            with st.spinner("Chispa está leyendo tus respuestas..."):
                lectura = ia.diagnostico_ia(list(S.diag.items()))   # 🤖 IA: diagnóstico
            if not lectura:  # modo demo
                pregunta1 = caso.es_pregunta(resp[0])
                lectura = ("Empezaste preguntando antes de proponer: es justo lo que hacen los buenos consultores. "
                           if pregunta1 else
                           "Tu primer impulso fue proponer. En el reto, intenta preguntar antes de dar soluciones. ")
                lectura += "En el reto vamos a practicar cómo estructurar una propuesta bajo presión."
            S.diag_lectura = lectura
            st.rerun()
    if S.diag_lectura:
        chispa_dice(html.escape(S.diag_lectura))
        if st.button("Aceptar el reto", type="primary"):
            S.chat = [{"role": "assistant", "content": caso.APERTURA}]
            S.inicio = time.time()
            ir(2)

# ================================================================ PASO 2 · RETO
elif S.paso == 2:
    t = minutos()
    restante = max(0, caso.LIMITE_MIN - t)
    st.subheader(f"Reto: {caso.EMPRESA}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Tiempo", f"{t:.0f} min", f"{restante:.0f} min restantes" if restante else "Tiempo cumplido",
              delta_color="off")
    c2.metric("Presupuesto", f"${caso.PRESUPUESTO_GIRO if S.giro else caso.PRESUPUESTO_INICIAL:,}")
    c3.metric("Pistas usadas", S.pistas)

    usuario = [m["content"] for m in S.chat if m["role"] == "user"]

    if S.fase == "conversacion":
        if S.giro:
            chispa_dice("<b>¡Cambió el escenario!</b> Esto pasa todo el tiempo en las empresas. "
                        "¿Qué de lo que tenías en mente ya no funciona con $60,000?", "giro")
        else:
            chispa_dice(caso.RETO)
        for m in S.chat:
            with st.chat_message("user" if m["role"] == "user" else "assistant",
                                 avatar=None if m["role"] == "user" else "🏺"):
                if m["role"] != "user":
                    st.markdown(f"**{caso.CLIENTE}** · {caso.CARGO}")
                st.write(m["content"])

        colp, cols = st.columns(2)
        if colp.button("Pedirle una pista a Chispa", disabled=S.pistas >= 3):
            S.pistas += 1
            resumen = (f"Ha hecho {len(usuario)} intervenciones; temas descubiertos: {', '.join(S.temas) or 'ninguno'}; "
                       f"giro ocurrido: {S.giro}.")
            with st.spinner("Chispa está pensando..."):
                pista = ia.tutor_ia("conversación con la clienta", resumen)   # 🤖 IA: tutora
            if not pista:
                if len([u for u in usuario if caso.es_pregunta(u)]) < 2:
                    pista = "Antes de proponer, entiende. ¿Qué te falta saber de sus clientes, su competencia o su meta?"
                elif "clientes" not in S.temas:
                    pista = "Pregúntale quién le compra y qué producto le deja más. A veces lo más rentable está escondido."
                elif "meta" not in S.temas:
                    pista = "¿Ya sabes cómo va a medir el éxito el consejo? Sin meta, no sabrás si tu plan funcionó."
                else:
                    pista = "Ya tienes buena información. De todo lo que te dijo, ¿qué es lo más importante?"
            S.ultima_pista = pista
            st.rerun()
        listo_para_proponer = len(usuario) >= 3
        if cols.button("Ya entendí el problema: armar propuesta", type="primary", disabled=not listo_para_proponer):
            S.fase = "propuesta"
            st.rerun()
        if not listo_para_proponer:
            st.caption("Haz al menos 3 intervenciones con Carmen antes de proponer.")
        if S.ultima_pista:
            st.markdown(chispa.burbuja(html.escape(S.ultima_pista), "pensando", 70), unsafe_allow_html=True)

        msg = st.chat_input("Escríbele a Carmen...")
        if msg:
            S.chat.append({"role": "user", "content": msg})
            ya_dichos = list(S.temas)
            S.temas.extend(k for k in caso.temas(msg) if k not in S.temas)
            with st.spinner("Carmen está escribiendo..."):
                resp = ia.cliente_ia(S.chat, caso.contexto_para_ia(S.giro), S.giro)   # 🤖 IA: clienta
            if not resp:
                resp, _ = caso.responder_demo(msg, S.giro, ya_dichos)
            S.chat.append({"role": "assistant", "content": resp})
            if not S.giro and len(usuario) + 1 >= caso.MENSAJES_ANTES_DEL_GIRO:
                S.giro = True
                S.chat.append({"role": "assistant", "content": caso.GIRO})
            st.rerun()

    elif S.fase == "propuesta":
        chispa_dice("Ahora, tu propuesta. Empieza por el <b>problema de fondo</b>, no por la solución. "
                    "Y recuerda: el presupuesto ahora es de <b>$60,000</b>.", "guia")
        with st.expander("Repasar la conversación con Carmen"):
            for m in S.chat:
                st.markdown(f"**{'Tú' if m['role'] == 'user' else caso.CLIENTE}:** {m['content']}")
        with st.form("f_propuesta"):
            problema = st.text_area("1. ¿Cuál es el problema de fondo?", height=80)
            propuesta = st.text_input("2. Tu propuesta en una frase (menos de 25 palabras)")
            acciones = st.text_area("3. Tres acciones concretas, una por renglón, con su costo aproximado", height=110)
            medicion = st.text_area("4. ¿Cómo lo medirías? (meta, indicador y fecha)", height=70)
            aporte = st.text_area("5. ¿Usaste IA para pensar tu propuesta? ¿Qué agregaste tú que la IA no te dio?",
                                  height=70)
            if st.form_submit_button("Presentar a Carmen", type="primary"):
                if not (problema.strip() and propuesta.strip() and acciones.strip()):
                    st.warning("Completa al menos el problema, la propuesta y las acciones.")
                else:
                    S.propuesta = dict(problema=problema, propuesta=propuesta, acciones=acciones,
                                       medicion=medicion, aporte=aporte)
                    S.fase = "defensa"
                    st.rerun()

    elif S.fase == "defensa":
        chispa_dice("Carmen te va a hacer dos preguntas difíciles, como en un consejo. "
                    "Responde corto: <b>primero tu respuesta, luego el porqué</b>.", "guia")
        st.markdown(f'<div class="pb-cliente"><b>Tu propuesta:</b> {html.escape(S.propuesta["propuesta"])}</div>',
                    unsafe_allow_html=True)
        with st.form("f_defensa"):
            r1 = st.text_area(f"**{caso.CLIENTE}:** {caso.DEFENSA[0]}", height=90)
            r2 = st.text_area(f"**{caso.CLIENTE}:** {caso.DEFENSA[1]}", height=90)
            if st.form_submit_button("Terminar el reto", type="primary"):
                if not (r1.strip() and r2.strip()):
                    st.warning("Responde las dos preguntas.")
                else:
                    S.defensa = [r1, r2]
                    S.fin = time.time()
                    transcripcion = "\n".join(f"{'Alumno' if m['role'] == 'user' else 'Carmen'}: {m['content']}"
                                              for m in S.chat)
                    metricas = dict(minutos=round(minutos(), 1), pistas=S.pistas, giro=S.giro,
                                    temas_descubiertos=S.temas)
                    with st.spinner("Chispa está evaluando cómo trabajaste..."):
                        st.markdown(chispa.sola("pensando", 110), unsafe_allow_html=True)
                        res = ia.evaluar_ia(transcripcion, S.propuesta,                        # 🤖 IA: evaluación
                                            dict(zip(caso.DEFENSA, S.defensa)), metricas, COMPETENCIAS)
                    S.modo = "IA" if res else "demo"
                    if not res:
                        res = evaluar_demo(dict(mensajes_usuario=usuario, temas=S.temas, propuesta=S.propuesta,
                                                defensa=S.defensa, minutos=minutos(), pistas=S.pistas))
                    S.resultado = res
                    S.racha += 1
                    ir(3)

# ================================================================ PASO 3 · RESULTADOS Y PORTAFOLIO
elif S.paso == 3:
    r, p = S.resultado, S.perfil
    if not S.celebrado:  # celebración una sola vez al llegar
        st.balloons()
        S.celebrado = True
    chispa_dice(f"<b>¡Lo lograste, {html.escape(p['nombre'])}!</b> Aquí no hay calificación: esto es cómo trabajaste "
                "y qué puedes mejorar. Todo queda en tu portafolio.", "logro", 120)

    niveles = [r["competencias"][c]["nivel"] for c in COMPETENCIAS]
    fig = go.Figure(go.Scatterpolar(r=niveles + niveles[:1], theta=COMPETENCIAS + COMPETENCIAS[:1], fill="toself",
                                    line_color="#1E6BE6", fillcolor="rgba(255,200,0,0.40)", name="Tú"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 4], tickvals=[1, 2, 3, 4],
                                                 ticktext=[NIVELES[i] for i in range(1, 5)])),
                      showlegend=False, height=420, margin=dict(l=70, r=70, t=30, b=30))
    st.plotly_chart(fig, width="stretch")

    for c in COMPETENCIAS:
        d = r["competencias"][c]
        st.markdown(f"**{c}: {NIVELES.get(int(d['nivel']), d['nivel'])}** — {d['evidencia']}")
        st.caption(RUBRICA[c])

    c1, c2 = st.columns(2)
    c1.markdown("#### Lo que hiciste bien")
    for f in r["fortalezas"]:
        c1.markdown(f"- {f}")
    c2.markdown("#### Lo que puedes mejorar")
    for m in r["mejoras"] or ["Sigue practicando con un encargo más difícil."]:
        c2.markdown(f"- {m}")
    st.markdown("#### Señales de proactividad")
    for s_ in r["senales_proactividad"]:
        st.markdown(f"- {s_}")
    st.info(f"**Siguiente paso:** {r['siguiente_paso']}")
    st.caption(f"Evaluado en modo {'IA' if S.modo == 'IA' else 'demo (reglas)'} · {minutos():.0f} minutos · "
               f"{S.pistas} pistas.")

    # Portafolio descargable
    filas = "".join(f"<tr><td>{c}</td><td>{NIVELES.get(int(r['competencias'][c]['nivel']))}</td>"
                    f"<td>{html.escape(r['competencias'][c]['evidencia'])}</td></tr>" for c in COMPETENCIAS)
    portafolio = f"""<!doctype html><html lang="es"><meta charset="utf-8"><title>Portafolio Starwise</title>
<body style="font-family:Arial,sans-serif;max-width:760px;margin:32px auto;color:#1B2430">
<h1 style="color:#1E6BE6">Portafolio Starwise · {html.escape(p['nombre'])}</h1>
<p>{html.escape(p['carrera'])} · {p['semestre']}° semestre · {dt.date.today():%d/%m/%Y}</p>
<h2>Encargo: {caso.EMPRESA}</h2>
<p>Recuperar ventas de un taller de talavera (−28%) antes del 31 de diciembre, sin despedir a nadie,
con un presupuesto que bajó de $150,000 a $60,000 a mitad del encargo.</p>
<h3>Mi propuesta</h3><p><b>{html.escape(S.propuesta.get('propuesta', ''))}</b></p>
<p><b>Problema de fondo:</b> {html.escape(S.propuesta.get('problema', ''))}</p>
<p><b>Acciones:</b><br>{html.escape(S.propuesta.get('acciones', '')).replace(chr(10), '<br>')}</p>
<p><b>Medición:</b> {html.escape(S.propuesta.get('medicion', ''))}</p>
<h3>Competencias demostradas</h3>
<table border="1" cellpadding="6" style="border-collapse:collapse">
<tr><th>Competencia</th><th>Nivel</th><th>Evidencia</th></tr>{filas}</table>
<h3>Señales de proactividad</h3><ul>{''.join(f'<li>{html.escape(x)}</li>' for x in r['senales_proactividad'])}</ul>
<p style="color:#6B7280;font-size:12px">Generado con Starwise (prototipo, hackathon Talavera Valley 2026).
Caso simulado con una empresa ficticia.</p></body></html>"""
    st.download_button("Descargar mi portafolio", portafolio.encode("utf-8"), "portafolio_starwise.html",
                       "text/html", type="primary")

    # Encuesta final → evidencia para "La prueba" del hackathon
    st.divider()
    st.markdown("#### Antes de irte (nos ayuda a mejorar)")
    if S.guardado:
        st.success("¡Gracias! Tu respuesta quedó registrada.")
    else:
        with st.form("f_encuesta"):
            despues = st.slider("Del 1 al 5, ¿qué tan listo te sientes ahora para una entrevista o un primer proyecto?",
                                1, 5, p["antes"])
            cv = st.radio("¿Pondrías este portafolio en tu CV?", ["Sí", "Tal vez", "No"], horizontal=True)
            comentario = st.text_area("¿Qué cambiarías?")
            if st.form_submit_button("Enviar"):
                fila = dict(fecha=dt.datetime.now().strftime("%Y-%m-%d %H:%M"), participante=p["nombre"],
                            carrera=p["carrera"], semestre=p["semestre"], antes=p["antes"], despues=despues,
                            cv=cv, comentario=comentario, minutos=round(minutos(), 1), pistas=S.pistas,
                            mensajes=len([m for m in S.chat if m["role"] == "user"]),
                            temas_descubiertos="|".join(S.temas), modo=S.modo,
                            **{c: r["competencias"][c]["nivel"] for c in COMPETENCIAS})
                EVIDENCIA.parent.mkdir(exist_ok=True)
                pd.DataFrame([fila]).to_csv(EVIDENCIA, mode="a", header=not EVIDENCIA.exists(), index=False)
                S.guardado = True
                st.rerun()
    if st.button("Hacer otro reto"):
        racha, perfil = S.racha, S.perfil
        for k, v in DEFAULTS.items():
            S[k] = v if not isinstance(v, (list, dict)) else type(v)()
        S.defensa, S.racha, S.perfil, S.paso = ["", ""], racha, perfil, 1
        st.rerun()
