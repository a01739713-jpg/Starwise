"""Pruebas de Carmen (casos.py), tutor (chispa.py/ia.py), evidencia y portafolio."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import casos  # noqa: E402
import chispa  # noqa: E402
import evidencia  # noqa: E402
import ia  # noqa: E402
import portafolio  # noqa: E402


def _nuevo():
    return {"turnos": 0, "revelados": [], "giro": False, "presupuesto": casos.PRESUPUESTO_INICIAL, "log": []}


def test_carmen_normaliza_tildes_y_revela_hechos():
    e = _nuevo()
    r = casos.carmen_responder("¿Quiénes son sus CLIENTES más importantes?", e)
    assert "segmentos" in r["hechos"]
    r2 = casos.carmen_responder("y los margenes y costos?", e)
    assert "margen" in r2["hechos"]
    assert r["texto"] != r2["texto"]


def test_carmen_no_revela_solucion():
    e = _nuevo()
    r = casos.carmen_responder("¿Cuál es la solución?", e)
    assert r["hechos"] == [] and r["texto"] in casos.RESPUESTAS_SOLUCION


def test_respuestas_variadas_y_giro_en_cuarto_turno():
    e = _nuevo()
    textos = [casos.carmen_responder(q, e)["texto"] for q in ["hola", "¿instagram?", "¿hoteles?"]]
    assert len(set(textos)) == 3 and not e["giro"]
    r4 = casos.carmen_responder("¿qué pasa con las bodas?", e)
    assert r4["giro_ahora"] and e["giro"] and e["presupuesto"] == 60_000
    assert "60,000" in r4["texto"]
    r5 = casos.carmen_responder("¿cuál es el presupuesto?", e)
    assert not r5["giro_ahora"] and "60,000" in r5["texto"]


def test_categorias_investigacion():
    assert casos.categorias_descubiertas(["segmentos", "instagram", "margen", "meta"]) == ["clientes", "costos", "canales", "meta"]


def test_tutor_reglas_25_escenarios_y_pistas_graduales():
    assert chispa.total_escenarios() >= 25
    p = [chispa.pista("m2", n) for n in (1, 2, 3)]
    assert len(set(p)) == 3 and "V-0072" not in " ".join(p)
    assert chispa.responder_reglas("¿qué es un KPI?", "m1")["intencion"] == "concepto"
    assert chispa.responder_reglas("dame la respuesta", "m1")["intencion"] == "pedir_respuesta"
    assert chispa.responder_reglas("dame una pista", "m1")["es_pista"]


def test_ia_sin_clave_usa_reglas_y_bloquea_en_pruebas(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    est = ia.estado_ia({})
    assert not est["disponible"] and est["etiqueta"] == ia.ETIQUETA_REGLAS
    r = ia.tutor("", "pista", {"fase": "practica", "mision": "m1", "nivel_pista": 2}, {})
    assert r["fuente"] == "reglas" and r["es_pista"]
    bloqueado = ia.tutor("ayuda", "libre", {"fase": "A", "mision": "m1"}, {})
    assert bloqueado["fuente"] == "bloqueado"


def test_ia_429_y_validacion(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "clave-falsa")

    class R:
        status_code = 429

    monkeypatch.setattr(ia.requests, "post", lambda *a, **k: R())
    control = {}
    r = ia.tutor("", "pista", {"fase": "practica", "mision": "m2", "nivel_pista": 1}, control)
    assert r["fuente"] == "reglas" and "429" in r["nota"]
    assert not ia.estado_ia(control)["disponible"]  # en enfriamiento
    assert ia._limpiar("La respuesta es V-0072, quítalo") is None
    assert ia._limpiar("¿Qué columna te ayudaría a ver si una venta se repite?")


def _S():
    S = {"intento": evidencia.nuevo_intento(), "tipo_registro": "interna", "escena": "cierre",
         "perfil": {"alias": "<script>alert(1)</script>", "intereses": ["Mercadotecnia"]},
         "autoeficacia_antes": 2, "autoeficacia_despues": 4, "pistas": {"m1": 1}, "tutor_log": [],
         "sim": {"giro": True, "presupuesto": 60000, "revelados": ["segmentos"], "archivos_abiertos": ["ventas"],
                 "hallazgos": {"anomalia_id": "V-0072", "anomalia_tipo": "Registro duplicado", "variacion_reportada": -28},
                 "planes": [{"montos": {"digital": 10000, "alianzas": 20000, "producto": 30000}, "total": 60000, "giro": True,
                             "presupuesto": 60000, "ts": "t"}],
                 "propuesta": {"diagnostico": "<img src=x onerror=alert(1)>", "datos_citados": [], "acciones": ["a"]}},
         "A": {}, "B": {}, "encuesta": {"relevancia": 5}}
    return S


def test_portafolio_escapa_html_y_no_atribuye_empleo():
    h = portafolio.portafolio_html(_S(), "Tutor demo por reglas")
    assert "<script>alert" not in h and "&lt;script&gt;" in h
    assert "<img src=x" not in h
    assert "no práctica laboral formal" in h
    frase = portafolio.frase_cv(_S())
    assert "simulación académica" in frase and "ficticia" in frase and "trabajé en" not in frase.lower()


def test_evidencia_json_dedup_y_sinteticos():
    S = _S()
    reg = evidencia.construir_registro(S, "reglas")
    assert reg["schema_version"] == evidencia.SCHEMA_VERSION and reg["rubric_version"]
    raw = evidencia.a_json(reg).encode()
    qa = evidencia.a_json(evidencia.registro_qa_sintetico()).encode()
    regs, err = evidencia.leer_registros([("a.json", raw), ("a_copia.json", raw), ("qa.json", qa), ("malo.json", b"{x")])
    assert len(err) == 1
    df = evidencia.consolidar(regs)
    assert len(df) == 2
    m = evidencia.metricas(df)
    assert m["n_reales"] == 1 and m["n_sinteticos_excluidos"] == 1
    assert json.loads(raw)["participante"]["alias"] == "<script>alert(1)</script>"  # dato fiel; se escapa al renderizar


def test_metricas_vacias():
    assert evidencia.metricas(evidencia.consolidar([]))["n_reales"] == 0
