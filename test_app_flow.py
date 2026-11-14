"""Prueba de humo con el AppTest oficial de Streamlit. Se omite si Streamlit no está instalado."""
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(Path(__file__).resolve().parents[1] / "app.py")
sys.path.insert(0, str(Path(APP).parent))


def _boton(at, key):
    return next(b for b in at.button if b.key == key)


def test_portada_y_perfil():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    _boton(at, "w_comenzar").click().run()
    assert at.session_state["S"]["escena"] == "perfil"
    at.checkbox(key="w_mayor").check()
    at.checkbox(key="w_consent").check()
    for b in at.button:
        if b.label == "Elegir misión":
            b.click().run()
            break
    assert not at.exception
    assert at.session_state["S"]["escena"] == "rutas"


def test_diagnostico_A_sin_tutor():
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    at.session_state["S"]["escena"] = "diag_A"
    at.run()
    assert not at.exception
    assert not [b for b in at.button if (b.key or "").startswith("w_pista")]
