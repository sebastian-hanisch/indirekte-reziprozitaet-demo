"""Permalink (Begrenzen und Einrasten), Presets."""

from dataclasses import dataclass

import streamlit as st

import ire_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: type
    default: object
    lo: float | None = None
    hi: float | None = None
    choices: tuple | None = None


SETTING_SPECS = {
    "norm_select": SettingSpec("norm", str, C.DEFAULT_NORM, choices=C.NORM_KEYS),
    "b_slider": SettingSpec("b", float, C.DEFAULT_B, C.B_MIN, C.B_MAX),
    "e1_slider": SettingSpec("e1", float, C.DEFAULT_E1, C.E1_MIN, C.E1_MAX),
    "e2_slider": SettingSpec("e2", float, C.DEFAULT_E2, C.E2_MIN, C.E2_MAX),
    "allc_slider": SettingSpec("allc", float, C.DEFAULT_ALLC, C.SHARE_MIN, C.SHARE_MAX),
    "alld_slider": SettingSpec("alld", float, C.DEFAULT_ALLD, C.SHARE_MIN, C.SHARE_MAX),
}
PRESET_KEYS = {"norm": "norm_select", "b": "b_slider", "e1": "e1_slider", "e2": "e2_slider", "allc": "allc_slider", "alld": "alld_slider"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def clamp(spec: SettingSpec, value):
    if spec.choices is not None:
        return value if value in spec.choices else spec.default
    return min(spec.hi, max(spec.lo, value))


def load_permalink_settings():
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param not in qp:
            continue
        raw = qp[spec.url_param]
        if isinstance(raw, list):
            raw = raw[0] if raw else ""
        try:
            value = spec.caster(raw)
        except (ValueError, TypeError):
            continue
        st.session_state[state_key] = clamp(spec, value)
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][key]
