"""Kern der Demo (numpy): indirekte Reziprozität mit öffentlicher Bewertung (Nowak und Sigmund 1998, Ohtsuki und Iwasa 2004).

Eine große Population, jede Runde trifft jeder einen zufälligen Empfänger und kann ihm helfen (Kosten c, Nutzen b). Alle sehen dieselbe Reputation (gut/schlecht).
Drei Strategien: Immer helfen (ALLC), Nie helfen (ALLD), Diskriminierer (DISC: hilft nur Guten). Eine Bewertungsregel legt fest, wer nach einer Handlung als gut gilt.
Einheiten (DEMO-PLAYBOOK §1b):

- `cooperation_probability`  Wahrscheinlichkeit zu helfen, je Strategie und Empfänger-Reputation (mit Ausführungsfehler e1)
- `reputations`             Anteil guter Spieler je Strategie und insgesamt, exakt (affine Gleichung in g)
- `payoffs`                 mittlere Auszahlung je Strategie
- `invasion_fitness`        Vorteil eines seltenen Eindringlings gegenüber der residenten Strategie
- `replicator_rhs`, `integrate`   Replikatordynamik auf dem Simplex"""

import numpy as np

import ire_constants as C


def cooperation_probability(strategy: str, recipient_good: bool, e1: float) -> float:
    """P(hilft) bei Ausführungsfehler e1: ALLC hilft immer, ALLD nie, DISC nur einem guten Empfänger; jeweils mit Wahrscheinlichkeit 1 − e1."""
    if strategy == "ALLC":
        return 1.0 - e1
    if strategy == "ALLD":
        return 0.0
    if strategy == "DISC":
        return (1.0 - e1) if recipient_good else 0.0
    raise ValueError(f"unbekannte Strategie {strategy}")


def reputations(shares: dict, norm: str, e1: float, e2: float) -> tuple[float, dict]:
    """(g, g_s): Anteil guter Spieler insgesamt und je Strategie im stationären Zustand.

    Ein Spieler gilt nach seiner letzten Handlung als gut, wenn die Regel d(Handlung, Empfänger) es sagt (mit Bewertungsfehler e2 umgekehrt). Für die Strategie s:
    P_gut(s) = (1−e2)·Q_s + e2·(1−Q_s) mit Q_s = g·q(s,gut) + (1−g)·q(s,schlecht): affin in g, also g = A / (1 − B) exakt.
    Gibt es keine eindeutige Lösung (B = 1, etwa Image Scoring ohne Fehler), ist jedes g stationär: ein ValueError."""
    rule = C.NORMS[norm]["rule"]
    d_cg, d_cb, d_dg, d_db = rule
    a_tot = b_tot = 0.0
    parts = {}
    for s in C.STRATEGY_KEYS:
        p_g, p_b = cooperation_probability(s, True, e1), cooperation_probability(s, False, e1)
        q_g = p_g * d_cg + (1.0 - p_g) * d_dg            # P(als gut bewertet | Empfänger gut)
        q_b = p_b * d_cb + (1.0 - p_b) * d_db            # P(als gut bewertet | Empfänger schlecht)
        a1, b1 = q_b, q_g - q_b                          # Q_s = a1 + b1·g
        u = (1.0 - e2) * a1 + e2 * (1.0 - a1)
        v = (1.0 - 2.0 * e2) * b1
        parts[s] = (u, v)
        a_tot += shares[s] * u
        b_tot += shares[s] * v
    if abs(1.0 - b_tot) < 1e-12:
        raise ValueError("Reputation unbestimmt: jedes g ist stationär")
    g = a_tot / (1.0 - b_tot)
    return g, {s: parts[s][0] + parts[s][1] * g for s in C.STRATEGY_KEYS}


def payoffs(shares: dict, norm: str, b: float, e1: float, e2: float, c: float = C.COST) -> dict:
    """Mittlere Auszahlung je Runde je Strategie: b · (erhaltene Hilfe) − c · (geleistete Hilfe)."""
    g, gs = reputations(shares, norm, e1, e2)
    out = {}
    for s in C.STRATEGY_KEYS:
        gives = g * cooperation_probability(s, True, e1) + (1.0 - g) * cooperation_probability(s, False, e1)
        gets = sum(shares[t] * (gs[s] * cooperation_probability(t, True, e1) + (1.0 - gs[s]) * cooperation_probability(t, False, e1)) for t in C.STRATEGY_KEYS)
        out[s] = b * gets - c * gives
    return {"f": out, "g": g, "gs": gs}


def monomorphic(strategy: str) -> dict:
    return {s: (1.0 if s == strategy else 0.0) for s in C.STRATEGY_KEYS}


def invasion_fitness(resident: str, invader: str, norm: str, b: float, e1: float, e2: float, eps: float = 1e-7) -> float:
    """f_Eindringling − f_Resident bei einem Anteil `eps` des Eindringlings: negativ heißt, er setzt sich nicht durch."""
    shares = {s: 0.0 for s in C.STRATEGY_KEYS}
    shares[resident], shares[invader] = 1.0 - eps, eps
    f = payoffs(shares, norm, b, e1, e2)["f"]
    return f[invader] - f[resident]


def replicator_rhs(x: np.ndarray, norm: str, b: float, e1: float, e2: float) -> np.ndarray:
    shares = dict(zip(C.STRATEGY_KEYS, x))
    f = payoffs(shares, norm, b, e1, e2)["f"]
    fit = np.array([f[s] for s in C.STRATEGY_KEYS])
    return x * (fit - float(x @ fit))


def integrate(x0, norm: str, b: float, e1: float, e2: float, t_max: float = C.TIME_MAX, dt: float = C.DT, record_every: int = C.RECORD_EVERY):
    """Runge-Kutta 4. Ordnung auf dem Simplex; gibt (Zeiten, Anteile) zurück, der Endzustand ist immer dabei."""
    x = np.array(x0, dtype=float)
    steps = int(round(t_max / dt))
    times, traj = [0.0], [x.copy()]
    for k in range(1, steps + 1):
        k1 = replicator_rhs(x, norm, b, e1, e2)
        k2 = replicator_rhs(x + 0.5 * dt * k1, norm, b, e1, e2)
        k3 = replicator_rhs(x + 0.5 * dt * k2, norm, b, e1, e2)
        k4 = replicator_rhs(x + dt * k3, norm, b, e1, e2)
        x = np.clip(x + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4), 0.0, None)
        x = x / x.sum()
        if k % record_every == 0 or k == steps:
            times.append(k * dt)
            traj.append(x.copy())
    return np.array(times), np.array(traj)


def initial_mix(allc: float, alld: float) -> np.ndarray:
    """Anfangsanteile (ALLC, ALLD, DISC); der Rest sind Diskriminierer."""
    if allc < 0 or alld < 0 or allc + alld > 1.0:
        raise ValueError("Anteile müssen in [0, 1] liegen und höchstens 1 ergeben")
    return np.array([allc, alld, 1.0 - allc - alld])
