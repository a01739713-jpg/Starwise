"""Lee el Repositorio EdTech del hackathon (data/repositorio.csv) y devuelve datos con su fuente."""
from pathlib import Path
import pandas as pd

RUTA = Path(__file__).parent / "data" / "repositorio.csv"


def cargar():
    try:
        return pd.read_csv(RUTA)
    except Exception:
        return pd.DataFrame(columns=["Bloque", "Tabla", "Dato", "Valor", "Comparación o nota", "Fuente", "Enlace"])


def dato(df, contiene):
    """Primer renglón cuyo 'Dato' contiene el texto dado. Regresa dict o None."""
    m = df[df["Dato"].astype(str).str.contains(contiene, case=False, regex=False)]
    if m.empty:
        return None
    r = m.iloc[0]
    return {"dato": r["Dato"], "valor": r["Valor"], "fuente": r["Fuente"],
            "enlace": r["Enlace"] if isinstance(r["Enlace"], str) else ""}


# Palabra clave de cada carrera de negocios → texto en la tabla de ingresos del Repositorio (IMCO 2026)
CARRERAS = {
    "Administración de empresas": None,
    "Mercadotecnia": None,
    "Finanzas": "Finanzas, banca y seguros",
    "Negocios internacionales": None,
    "Emprendimiento / innovación": None,
    "Contaduría": None,
    "Otra": None,
}


def tarjeta_carrera(df, carrera):
    """Datos que se muestran al alumno en el diagnóstico (todos salen del Repositorio)."""
    datos = []
    clave = CARRERAS.get(carrera)
    ingreso = dato(df, clave) if clave else None
    if ingreso:
        datos.append(("Ingreso promedio en tu campo", ingreso))
    else:
        prom = dato(df, "Ingreso mensual promedio")
        if prom:
            datos.append(("Ingreso promedio de un profesionista", prom))
    for etiqueta, clave in [
        ("Trabajan fuera de lo que estudiaron", "Profesionistas que trabajan fuera de lo que estudiaron"),
        ("…y ganan menos que quien sí ejerce", "Cuánto menos ganan quienes trabajan fuera de su campo"),
        ("Primer salario de hasta $10,000 al mes", "Egresados cuyo primer salario"),
        ("Costo de 4 años en universidad pública (Ruta Base)", "Costo directo en pública"),
        ("Costo de 4 años en universidad privada (Ruta Base)", "Costo directo en privada"),
    ]:
        d = dato(df, clave)
        if d:
            datos.append((etiqueta, d))
    return datos
