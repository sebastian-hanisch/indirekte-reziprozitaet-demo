"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: laedt app.py mit den
Standardeinstellungen, klickt jeden Preset-Button und faehrt jeden Slider an seine Grenzen und prueft, dass
kein Python-Fehler auftritt - insbesondere `streamlit.errors.StreamlitDuplicateElementId` (mehrere
st.plotly_chart-Aufrufe ohne eindeutiges key= koennen zufaellig identischen Inhalt rendern und kollidieren)
und `StreamlitAPIException` bei Slidern mit berechneten Grenzen (min == max)."""

import os

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = 180
AUTOPLAY_MARKER = "\u25b6"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert labels, "keine Slider gefunden"
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


def test_permalink_is_clamped_and_snapped():
    at = AppTest.from_file(APP_PATH)
    at.query_params["norm"] = "XX"
    at.query_params["b"] = "99"
    at.query_params["e1"] = "-1"
    at.query_params["allc"] = "5"
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert at.session_state["norm_select"] == "SJ"
    assert at.session_state["b_slider"] == 10.0
    assert at.session_state["e1_slider"] == 0.0
    assert at.session_state["allc_slider"] == 0.45


def test_the_page_explains_strategies_and_norms():
    at = _fresh_app()
    text = " ".join(m.value for m in at.markdown)
    for label in ("Immer helfen", "Nie helfen", "Diskriminierer", "Image Scoring", "Stern Judging", "Simple Standing", "Shunning"):
        assert label in text, label
    assert any("stabil" in s.value for s in at.success)


def test_image_scoring_without_errors_warns_instead_of_raising():
    at = AppTest.from_file(APP_PATH)
    at.query_params["norm"] = "IS"
    at.query_params["e1"] = "0"
    at.query_params["e2"] = "0"
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert any("unbestimmt" in w.value for w in at.warning)
