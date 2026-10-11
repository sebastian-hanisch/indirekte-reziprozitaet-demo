"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Permalink-Begrenzen und Einrasten."""

import ire_constants as C
import ire_evaluation as ev
import ire_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, p in C.PRESETS.items():
        assert p["norm"] in C.NORM_KEYS, name
        assert C.B_MIN <= p["b"] <= C.B_MAX and C.E1_MIN <= p["e1"] <= C.E1_MAX and C.E2_MIN <= p["e2"] <= C.E2_MAX, name
        assert C.SHARE_MIN <= p["allc"] <= C.SHARE_MAX and C.SHARE_MIN <= p["alld"] <= C.SHARE_MAX and p["allc"] + p["alld"] < 1.0, name


def test_default_preset_equals_the_default_settings():
    first = next(iter(C.PRESETS.values()))
    assert ev.Settings(first["norm"], first["b"], first["e1"], first["e2"], first["allc"], first["alld"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_clamp_limits_numbers_and_snaps_choices():
    assert P.clamp(P.SETTING_SPECS["b_slider"], 99.0) == C.B_MAX
    assert P.clamp(P.SETTING_SPECS["norm_select"], "SS") == "SS" and P.clamp(P.SETTING_SPECS["norm_select"], "XX") == C.DEFAULT_NORM


def test_preset_stories_hold():
    def run(name):
        p = C.PRESETS[name]
        return ev.analyse(ev.Settings(p["norm"], p["b"], p["e1"], p["e2"], p["allc"], p["alld"]))

    assert run("Stern Judging, wenige Fehler").winner == "DISC"
    assert run("Simple Standing, wenige Fehler").winner == "DISC"
    im = run("Image Scoring, wenige Fehler")
    assert im.final[0] > 0.5 and im.winner is None
    sh = run("Shunning, wenige Fehler")
    assert sh.mono["g"] < 0.5 and sh.winner == "DISC"                         # stabil, aber wenig guter Ruf
    assert run("Stern Judging, viele Fehler (10 %)").winner == "DISC"
