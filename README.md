# Starwise · prototipo

**Data Spark · Talavera Valley Hackathon 2026 · Track 03 EdTech**

Starwise le da a los universitarios experiencia práctica documentada antes de su primer empleo.
Chispa, nuestra guía, te pone frente al problema real de una empresa, te acompaña mientras lo
resuelves y al final te entrega retroalimentación por competencias y un portafolio para tu CV.

## Qué hace el prototipo

1. **Perfil:** carrera, semestre, intereses y autoevaluación inicial, con consentimiento si eres menor de 18.
2. **Diagnóstico:** muestra datos reales del Repositorio EdTech para tu carrera (ingreso, % que trabaja
   fuera de su campo, costo de la Ruta Base) y 3 situaciones rápidas que la IA lee.
3. **Reto con cliente IA:** Carmen Ruiz, directora de *Talavera Viva* (empresa ficticia), necesita
   recuperar ventas (−28%) antes del 31 de diciembre. El alumno pregunta, descubre información oculta,
   enfrenta un **giro** (el presupuesto baja de $150,000 a $60,000), arma su propuesta y la **defiende**.
   Tiene un límite de 20 minutos y Chispa da hasta 3 pistas.
4. **Resultados:** un radar con 5 competencias **sin calificación**, evidencia, señales de proactividad,
   el siguiente paso y un portafolio descargable.
5. **Encuesta final:** se guarda como evidencia para "La prueba" (panel del equipo en la barra lateral).

## 🤖 Dónde está la IA

Toda la IA está en **`ia.py`**. En `app.py`, cada llamada está marcada con `# 🤖 IA:`.

| Función | Qué hace la IA |
| --- | --- |
| `cliente_ia()` | Interpreta a Carmen, la clienta: responde solo lo que le preguntan y cuestiona propuestas débiles |
| `tutor_ia()` | Es Chispa: da pistas socráticas sin dar la respuesta |
| `diagnostico_ia()` | Lee las 3 situaciones y detecta el punto de partida |
| `evaluar_ia()` | Evalúa la conversación, la propuesta y la defensa con la rúbrica, y devuelve evidencia |

**Sin API key la app funciona igual, en "modo demo":** Carmen responde por reglas (`caso.py`) y la
evaluación usa la rúbrica por reglas (`evaluacion.py`). Chispa se anima mientras "piensa", que es lo
que en la versión con IA corresponde a la llamada al modelo.

## Correrlo en tu computadora

```
pip install -r requirements.txt
streamlit run app.py
```

Se abre en el navegador, en `http://localhost:8501`.

## Publicarlo con link (para la prueba con usuarios y el jurado)

1. Sube esta carpeta a su repositorio de GitHub (por ejemplo, dentro de `codigo/`).
2. Entra a **share.streamlit.io** con tu GitHub → **Create app** → elige el repo, la rama y el archivo
   `app.py` (o `codigo/app.py`).
3. Deploy. Te da un link `https://<nombre>.streamlit.app`. Hagan un QR con ese link para el pitch.

## (Opcional) Activar la IA real gratis

1. Entra a Google AI Studio con una cuenta de Google y crea una API key. Revisen las condiciones de la
   capa gratuita vigente antes de usarla.
2. En Streamlit Cloud: tu app → **Settings → Secrets** y pega:
   ```
   GEMINI_API_KEY = "tu-key"
   ```
   En local: copia `.streamlit/secrets.toml.example` como `.streamlit/secrets.toml`.
3. **Nunca subas la key a GitHub.** `secrets.toml` ya está en `.gitignore`.

Si la key falla (sin internet o sin cuota), la app regresa sola al modo demo.

## La prueba con usuarios

- Pásenle el link a 5–10 universitarios fuera del equipo. Cada uno hace el reto completo (unos 20 min).
- La encuesta final registra: autoevaluación antes y después, si lo pondrían en su CV, comentarios,
  minutos, pistas, temas descubiertos y nivel por competencia.
- En la barra lateral, **Panel del equipo → Descargar evidencia (CSV)** y guárdenlo en `evidencia/`.
- ⚠️ En Streamlit Cloud el archivo se borra si la app se reinicia: **descarguen el CSV después de cada
  ronda de pruebas.**

## Guion del demo (2–3 minutos)

1. Perfil → diagnóstico: muestren la tarjeta con datos del Repositorio (cumple el requisito del dato).
2. Reto: escriban, por ejemplo, *"¿Por qué cayeron las ventas?"*, *"¿Quiénes son sus clientes?"* (aparece
   el hallazgo de las vajillas de boda) y *"¿Cuál es la meta del consejo?"*. Con la cuarta intervención
   llega **el giro** y Chispa cambia de estado.
3. Propuesta y defensa (tengan textos listos para pegar).
4. Resultados: el radar, las señales de proactividad y el portafolio.

## Estructura

```
app.py           Pantallas y flujo (Streamlit)
ia.py            🤖 Toda la IA (Gemini); sin key regresa None → modo demo
caso.py          Caso Talavera Viva: hechos, giro, defensa y cliente por reglas
evaluacion.py    Rúbrica de 5 competencias y evaluación por reglas
datos.py         Lectura del Repositorio EdTech (data/repositorio.csv)
chispa.py        Chispa en SVG con animaciones por estado
assets/          Imágenes de Chispa
evidencia/       sesiones.csv (se crea con la encuesta)
```

*El caso usa una empresa ficticia. Starwise no otorga validez oficial de estudios.*
