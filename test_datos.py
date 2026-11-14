"""Pruebas de datos.py: validación del repositorio y reconciliación de los datos sintéticos.

El CSV de estas pruebas es un FIXTURE de prueba construido aquí; no sustituye al CSV oficial.
"""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import casos  # noqa: E402
import datos  # noqa: E402

ENC = ",".join(datos.COLUMNAS_REPO)


def _csv(filas, encabezado=ENC, sep=","):
    lineas = [encabezado.replace(",", sep)]
    for f in filas:
        lineas.append(sep.join(f'"{c}"' for c in f))
    return "\n".join(lineas)


FILAS_OK = [
    ["03", "Primer empleo", "Egresados cuyo primer salario fue de hasta $10,000 al mes (ENE 2025)", "69.5%", "", "UVM", "https://www.prensa-ejemplo.com/nota"],
    ["03", "Primer empleo", "Egresados sin prestaciones en su primer empleo / en su empleo actual (ENE 2025)", "30.4% / 16.3%", "", "UVM", "https://www.uvm.mx/ene"],
    ["04", "Costos", "Costo directo en pública", "≈ $55,296", "", "Ref.", ""],
]


def test_lee_y_verifica_indicadores_exactos():
    res = datos.leer_repositorio(_csv(FILAS_OK).encode("utf-8"))
    assert res["estado"] == "ok" and res["filas"] == 3
    ind = datos.validar_indicadores(res["df"])
    assert ind["primer_salario_10k"]["estado"] == "verificado"
    assert ind["primer_salario_10k"]["calidad"] == "Referencia secundaria"
    sp = ind["sin_prestaciones"]
    assert sp["estado"] == "verificado" and sp["valor_mostrado"] == "30.4%"
    assert sp["calidad"].startswith("Fuente original")
    assert ind["costo_publica"]["estado"] == "verificado"
    assert ind["ingreso_promedio"]["estado"] == "no_encontrado"


def test_valor_distinto_no_se_verifica():
    filas = [r[:] for r in FILAS_OK]
    filas[1][3] = "31.0% / 16.3%"
    ind = datos.validar_indicadores(datos.leer_repositorio(_csv(filas).encode())["df"])
    assert ind["sin_prestaciones"]["estado"] == "valor_distinto"


def test_sin_fuzzy_matching():
    filas = [["03", "x", "Egresados sin prestaciones en su primer empleo (ENE 2025)", "30.4%", "", "", ""]]
    ind = datos.validar_indicadores(datos.leer_repositorio(_csv(filas).encode())["df"])
    assert ind["sin_prestaciones"]["estado"] == "no_encontrado"


def test_etiqueta_repetida_con_valores_distintos_es_ambigua():
    filas = FILAS_OK + [["09", "x", FILAS_OK[0][2], "70%", "", "", ""]]
    ind = datos.validar_indicadores(datos.leer_repositorio(_csv(filas).encode())["df"])
    assert ind["primer_salario_10k"]["estado"] == "ambiguo"


def test_encabezados_invalidos():
    res = datos.leer_repositorio(_csv(FILAS_OK, "Bloque,Tabla,Dato,Valor,Nota,Fuente,Enlace").encode())
    assert res["estado"] == "encabezados_invalidos" and "Comparación o nota" in res["mensaje"]


def test_encoding_cp1252_y_punto_y_coma():
    res = datos.leer_repositorio(_csv(FILAS_OK, sep=";").encode("cp1252", errors="replace"))
    assert res["estado"] == "ok" and res["separador"] == ";"


def test_bom_utf8():
    res = datos.leer_repositorio(_csv(FILAS_OK).encode("utf-8-sig"))
    assert res["estado"] == "ok" and "Bloque" in res["df"].columns


def test_csv_ausente(tmp_path):
    res = datos.leer_repositorio(tmp_path / "no_existe.csv")
    assert res["estado"] == "ausente" and res["df"] is None
    assert all(v["estado"] == "sin_csv" for v in datos.validar_indicadores(None).values())


def test_ventas_reconcilian_con_relato():
    v = datos.cargar_sintetico("ventas_talavera.csv")
    assert datos.id_duplicado(v) == ["V-0072"]
    limpio = datos.resumen_trimestres(datos.limpiar_duplicados(v))
    assert limpio["T2"] == 1_250_000 and limpio["T3"] == 900_000
    assert limpio["variacion_pct"] == pytest.approx(-28.0)
    crudo = datos.resumen_trimestres(v)["variacion_pct"]
    assert abs(crudo - (-28.0)) > 1  # el duplicado cambia el resultado: la anomalía importa
    seg = datos.variacion_por(datos.limpiar_duplicados(v), "segmento").set_index("segmento")["variación_%"]
    assert seg.idxmin() == "Restaurantes" and seg["Restaurantes"] == pytest.approx(-38.1)
    assert (v["importe_mxn"] > 0).all()


def test_hechos_del_caso_coinciden_con_datos():
    v = datos.limpiar_duplicados(datos.cargar_sintetico("ventas_talavera.csv"))
    ig = v[v["canal"] == "Instagram"]["importe_mxn"].sum() / v["importe_mxn"].sum()
    assert ig < 0.05  # Carmen: «menos del 5 %»
    costos = datos.cargar_sintetico("costos_talavera.csv").set_index("producto")
    assert costos.loc["Pieza personalizada", "margen_bruto_pct"] == 55.0
    assert costos["margen_bruto_pct"].idxmin() == "Azulejo"
    assert costos.loc["Pieza personalizada", "entrega_semanas_con_stock"] == 5
    cl = datos.cargar_sintetico("clientes_talavera.csv").set_index("segmento")
    assert (cl.loc["Restaurantes", "clientes_activos_T2"], cl.loc["Restaurantes", "clientes_activos_T3"]) == (14, 11)
    assert "−38.1 %" in casos.HALLAZGOS_DATOS["seg_restaurantes"]


def test_archivos_csv_iguales_a_generadores():
    for nombre, gen in datos.GENERADORES.items():
        p = datos.DATA_DIR / nombre
        assert p.exists(), nombre
        pd.testing.assert_frame_equal(pd.read_csv(p, keep_default_na=False), gen(), check_dtype=False)


def test_microcasos_A_y_B_distintos_y_comparables():
    a, b = datos.micro_resumen(datos.generar_micro("A")), datos.micro_resumen(datos.generar_micro("B"))
    assert a["variacion_total_pct"] != b["variacion_total_pct"]
    assert a["segmento_mayor_caida"] == "Norte" and b["segmento_mayor_caida"] == "Papelería"
    assert set(datos.generar_micro("A").columns) == set(datos.generar_micro("B").columns)
