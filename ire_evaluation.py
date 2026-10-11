"""Kennzahlen, Verdikt-Logik und Auswertungen über den Kern (die Komposition der Einheiten aus ire_algorithm)."""

from dataclasses import dataclass

import ire_algorithm as A
import ire_constants as C


def fmt(x: float, digits: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


@dataclass(frozen=True)
class Settings:
    norm: str = C.DEFAULT_NORM
    b: float = C.DEFAULT_B
    e1: float = C.DEFAULT_E1
    e2: float = C.DEFAULT_E2
    allc: float = C.DEFAULT_ALLC
    alld: float = C.DEFAULT_ALLD


@dataclass(frozen=True)
class Analysis:
    times: tuple[float, ...]
    shares: tuple[tuple[float, ...], ...]
    final: tuple[float, ...]
    winner: str | None                       # Strategie mit über 90 % Endanteil, sonst None (Mischzustand)
    mono: dict | None                        # Auszahlungen und Reputation in der reinen Diskriminierer-Population; None, wenn unbestimmt
    invasion_allc: float | None
    invasion_alld: float | None
    determined: bool


def analyse(settings: Settings) -> Analysis:
    """Dynamik aus den eingestellten Anfangsanteilen und Stabilität der reinen Diskriminierer-Population.

    Ist die Reputation unbestimmt (jedes g ist stationär: Image Scoring oder Shunning ohne Fehler), gibt es keinen Schwerpunkt; `determined` ist dann False. Das kann schon
    entlang der Dynamik auftreten (die Population läuft in die reine Diskriminierer-Population) oder erst bei der Stabilitätsprüfung."""
    x0 = A.initial_mix(settings.allc, settings.alld)
    try:
        times, traj = A.integrate(x0, settings.norm, settings.b, settings.e1, settings.e2)
        mono = A.payoffs(A.monomorphic("DISC"), settings.norm, settings.b, settings.e1, settings.e2)
        inv_allc = A.invasion_fitness("DISC", "ALLC", settings.norm, settings.b, settings.e1, settings.e2)
        inv_alld = A.invasion_fitness("DISC", "ALLD", settings.norm, settings.b, settings.e1, settings.e2)
    except ValueError:
        return Analysis((), (), (), None, None, None, None, False)
    final = traj[-1]
    winner = None
    for s, v in zip(C.STRATEGY_KEYS, final):
        if v > 0.9:
            winner = s
    return Analysis(
        times=tuple(float(t) for t in times), shares=tuple(tuple(float(v) for v in row) for row in traj), final=tuple(float(v) for v in final),
        winner=winner, mono=mono, invasion_allc=inv_allc, invasion_alld=inv_alld, determined=True,
    )


def stability_table(b: float, e1: float, e2: float) -> list[dict]:
    """Je Bewertungsregel: Reputation und Auszahlung in der reinen Diskriminierer-Population und die Invasionsvorteile von ALLC und ALLD."""
    rows = []
    for norm in C.NORM_KEYS:
        try:
            m = A.payoffs(A.monomorphic("DISC"), norm, b, e1, e2)
            rows.append({"norm": norm, "label": C.NORMS[norm]["label"], "g": m["g"], "f": m["f"]["DISC"],
                         "allc": A.invasion_fitness("DISC", "ALLC", norm, b, e1, e2), "alld": A.invasion_fitness("DISC", "ALLD", norm, b, e1, e2), "determined": True})
        except ValueError:
            rows.append({"norm": norm, "label": C.NORMS[norm]["label"], "g": None, "f": None, "allc": None, "alld": None, "determined": False})
    return rows


def start_points(n_per_edge: int = 3) -> list[tuple[float, float]]:
    """Anfangspunkte (ALLC-Anteil, ALLD-Anteil) im Inneren des Simplex für die Trajektorien-Karte."""
    pts = []
    for i in range(1, n_per_edge + 1):
        for j in range(1, n_per_edge + 1):
            x, y = i / (n_per_edge + 1), j / (n_per_edge + 1)
            if x + y < 0.95:
                pts.append((round(x, 3), round(y, 3)))
    return pts


def trajectories(settings: Settings, n_per_edge: int = 3) -> list[dict]:
    out = []
    for allc, alld in start_points(n_per_edge):
        try:
            _, traj = A.integrate(A.initial_mix(allc, alld), settings.norm, settings.b, settings.e1, settings.e2)
        except ValueError:
            return []
        out.append({"start": (allc, alld), "path": [tuple(float(v) for v in row) for row in traj], "end": tuple(float(v) for v in traj[-1])})
    return out


def verdict(an: Analysis, settings: Settings) -> tuple[str, str]:
    label = C.NORMS[settings.norm]["label"]
    if not an.determined:
        return "warning", (f"Bei {label} ohne Fehler ist die Reputation **unbestimmt**: jeder Anteil guter Spieler ist stationär, die Rechnung hat keinen Schwerpunkt. "
                           "Schon kleine Fehler legen sie fest (Regler e1, e2).")
    f_mono = an.mono["f"]["DISC"]
    stable = an.invasion_allc is not None and an.invasion_allc < -C.TOL and an.invasion_alld < -C.TOL
    if stable:
        return "success", (f"{label}: Eine reine Diskriminierer-Population ist **stabil**. Sie erreicht {fmt(an.mono['g'] * 100, 0)} % guten Ruf und {fmt(f_mono)} Punkte je Runde; "
                           f"Immer-helfen verliert {fmt(-an.invasion_allc, 3)}, Nie-helfen {fmt(-an.invasion_alld, 3)} je Runde, wenn sie selten sind.")
    reason = "Immer-helfen" if (an.invasion_allc is not None and an.invasion_allc >= -C.TOL) else "Nie-helfen"
    return "warning", (f"{label}: Eine reine Diskriminierer-Population ist **nicht stabil**: {reason} hat einen Vorteil von "
                       f"{fmt(max(an.invasion_allc, an.invasion_alld), 3)} je Runde. Der guten Reputation ({fmt(an.mono['g'] * 100, 0)} %) steht {fmt(f_mono)} Punkte gegenüber.")
