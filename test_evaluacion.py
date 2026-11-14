"""Pruebas de evaluacion.py: criterios deterministas, sin proxies de longitud ni rapidez."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import datos  # noqa: E402
import evaluacion as ev  # noqa: E402

A = datos.generar_micro("A")
B = datos.generar_micro("B")


def _estado(res, cid):
    return next(c["estado"] for c in res["criterios"] if c["id"] == cid)


def test_respuesta_correcta_A():
    r = ev.evaluar_micro("A", A, {"variacion_pct": -12.9, "segmento": "Norte", "indicador": "clientes_ticket",
                                  "justificacion": "Norte cayó 30%. Revisaría sus clientes."})
    assert r["logrados"] == 4 and r["total_objetivos"] == 4
    assert _estado(r, "texto") == ev.REVISION
    assert r["nivel"] == "Aplicado en el caso"


def test_tolerancia_y_signo():
    ok = ev.evaluar_micro("A", A, {"variacion_pct": "-13,3"})
    assert _estado(ok, "calculo") == ev.LOGRADO  # dentro de ±0.5
    fuera = ev.evaluar_micro("A", A, {"variacion_pct": -13.5})
    assert _estado(fuera, "calculo") == ev.NO_OBSERVADO
    signo = ev.evaluar_micro("A", A, {"variacion_pct": 12.9})
    assert _estado(signo, "calculo") == ev.NO_OBSERVADO and "signo" in signo["criterios"][0]["evidencia"]


def test_longitud_no_otorga_puntos():
    corta = ev.evaluar_micro("B", B, {"justificacion": "Bajó 35%."})
    larga = ev.evaluar_micro("B", B, {"justificacion": "porque " * 60 + "es muy importante mejorar todo"})
    assert _estado(corta, "cifra") == ev.LOGRADO
    assert _estado(larga, "cifra") == ev.NO_OBSERVADO
    assert larga["logrados"] <= corta["logrados"]


def test_cifras_en_texto():
    assert ev.numeros_en_texto("Pasó de 63 mil a $72,800 y cayó −30 %") == [63000.0, 72800.0, -30.0]
    assert ev.contiene_cifra_del_caso("vendió 121,500", [121500])
    assert not ev.contiene_cifra_del_caso("vendió mucho", [121500])


def test_comparacion_solo_con_ambas_y_sin_causalidad():
    a = ev.evaluar_micro("A", A, {"variacion_pct": -20, "segmento": "Sur"})
    assert ev.comparar_AB(a, None) is None
    b = ev.evaluar_micro("B", B, {"variacion_pct": -15.7, "segmento": "Papelería", "indicador": "likes"})
    comp = ev.comparar_AB(a, b)
    cambios = {f["id"]: f["cambio"] for f in comp["filas"]}
    assert cambios["calculo"] == "Observado en B, no en A"
    assert cambios["indicador"] == "No observado en ninguna"
    assert "no demuestra" in comp["nota"].lower()


def _sim_completa():
    return {
        "revelados": ["segmentos", "margen", "instagram", "meta"], "archivos_abiertos": ["ventas", "clientes", "costos"],
        "filtros_usados": True, "giro": True, "presupuesto": 60_000,
        "hallazgos": {"variacion_reportada": -28.0, "segmento": "Restaurantes", "anomalia_id": "V-0072",
                      "anomalia_tipo": "Registro duplicado"},
        "planes": [{"montos": {"digital": 50000, "alianzas": 50000, "producto": 50000}, "total": 150000, "giro": False, "presupuesto": 150000},
                   {"montos": {"digital": 10000, "alianzas": 30000, "producto": 20000}, "total": 60000, "giro": True, "presupuesto": 60000}],
        "ajuste_justificacion": "Recorté la campaña digital.",
        "propuesta": {"diagnostico": "Cayeron restaurantes", "datos_citados": ["a", "b"], "solucion": "Reposición rápida",
                      "acciones": ["x", "y", "z"], "accion_prioritaria": "Mejora", "segmento_prioritario": "Restaurantes",
                      "justificacion_prioridad": "Es lo que más cayó", "kpi": "Restaurantes recuperados", "meta": "2 en 30 días"},
    }


def test_simulacion_completa():
    r = ev.evaluar_simulacion(_sim_completa())
    for area in ("investigacion", "analisis", "adaptacion"):
        assert r["areas"][area]["nivel"] == "Aplicado en el caso", area
    assert "Ajustó su presupuesto cuando cambió la restricción." in r["conductas"]


def test_simulacion_vacia_no_inventa():
    r = ev.evaluar_simulacion({})
    for a in r["areas"].values():
        assert all(c["estado"] != ev.LOGRADO for c in a["criterios"])
    assert r["conductas"] == []


def test_mas_acciones_o_texto_no_suben_nivel():
    s = _sim_completa()
    s["propuesta"]["solucion"] = "palabra " * 300
    s2 = _sim_completa()
    assert ev.evaluar_simulacion(s)["areas"]["comunicacion"]["nivel"] == ev.evaluar_simulacion(s2)["areas"]["comunicacion"]["nivel"]


def test_excede_presupuesto():
    s = _sim_completa()
    s["planes"][-1]["total"] = 65_000
    r = ev.evaluar_simulacion(s)["areas"]
    assert next(c for c in r["adaptacion"]["criterios"] if c["id"] == "ad_dentro")["estado"] == ev.NO_OBSERVADO
