"""Orakel-Tests indirekte-reziprozitaet-demo: der Kern wird gegen UNABHÄNGIGE Rechenwege geprüft (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §2).

1. Agentenbasierte Simulation einer endlichen Population (N = 6000) mit öffentlicher Reputation: Reputation je Strategie und mittlere Auszahlung gegen die exakten Werte.
2. Die Reputationsgleichung als Fixpunkt: g aus A/(1 − B) gegen Iteration g ← F(g) bis zur Konvergenz.
3. Die Replikatordynamik gegen scipy.integrate.solve_ivp."""

import numpy as np
import pytest

import ire_algorithm as A
import ire_constants as C

KEYS = C.STRATEGY_KEYS


def simulate_population(shares, norm, b, e1, e2, n=6000, rounds=160, burn=60, seed=5):
    """Jeder Spieler ist je Runde einmal Spender gegenüber einem zufälligen anderen. Reputation (gut/schlecht) wird synchron nach der Runde neu bewertet."""
    rng = np.random.default_rng(seed)
    counts = (np.array([shares[s] for s in KEYS]) * n).astype(int)
    counts[-1] += n - counts.sum()
    strat = np.repeat(np.arange(3), counts)                       # 0 ALLC, 1 ALLD, 2 DISC
    rep = np.ones(n, dtype=bool)                                  # alle starten gut
    d_cg, d_cb, d_dg, d_db = C.NORMS[norm]["rule"]
    good_sum = np.zeros(3)
    payoff_sum = np.zeros(3)
    measured = 0
    for r in range(rounds):
        recipient = rng.integers(0, n - 1, size=n)
        recipient = recipient + (recipient >= np.arange(n))       # nie sich selbst
        rec_good = rep[recipient]
        wants = np.where(strat == 0, True, np.where(strat == 1, False, rec_good))
        helps = wants & (rng.random(n) >= e1)
        received = np.bincount(recipient[helps], minlength=n)
        pay = b * received - C.COST * helps
        d = np.where(helps, np.where(rec_good, d_cg, d_cb), np.where(rec_good, d_dg, d_db)).astype(bool)
        flip = rng.random(n) < e2
        rep = np.where(flip, ~d, d)
        if r >= burn:
            for s in range(3):
                sel = strat == s
                if sel.any():
                    good_sum[s] += rep[sel].mean()
                    payoff_sum[s] += pay[sel].mean()
            measured += 1
    return good_sum / measured, payoff_sum / measured


@pytest.mark.parametrize("norm", ["SJ", "SS", "IS", "SH"])
def test_exact_reputation_and_payoff_match_an_agent_based_simulation(norm):
    shares = {"ALLC": 0.2, "ALLD": 0.2, "DISC": 0.6}
    b, e1, e2 = 3.0, 0.05, 0.05
    exact = A.payoffs(shares, norm, b, e1, e2)
    good, pay = simulate_population(shares, norm, b, e1, e2)
    for i, s in enumerate(KEYS):
        assert good[i] == pytest.approx(exact["gs"][s], abs=0.03), (norm, s)
        assert pay[i] == pytest.approx(exact["f"][s], abs=0.08), (norm, s)


def test_fixed_point_equals_the_iteration():
    shares = {"ALLC": 0.1, "ALLD": 0.3, "DISC": 0.6}
    for norm in C.NORM_KEYS:
        d_cg, d_cb, d_dg, d_db = C.NORMS[norm]["rule"]
        e1, e2 = 0.04, 0.03
        g = 0.5
        for _ in range(5000):
            total = 0.0
            for s in KEYS:
                p_g, p_b = A.cooperation_probability(s, True, e1), A.cooperation_probability(s, False, e1)
                q = g * (p_g * d_cg + (1 - p_g) * d_dg) + (1 - g) * (p_b * d_cb + (1 - p_b) * d_db)
                total += shares[s] * ((1 - e2) * q + e2 * (1 - q))
            g = total
        assert A.reputations(shares, norm, e1, e2)[0] == pytest.approx(g, abs=1e-9), norm


def test_replicator_matches_scipy():
    solve_ivp = pytest.importorskip("scipy.integrate").solve_ivp
    for norm in ("SJ", "IS"):
        x0 = np.array([0.1, 0.2, 0.7])
        times, traj = A.integrate(x0, norm, 3.0, 0.03, 0.03, t_max=40.0, dt=0.05, record_every=40)
        sol = solve_ivp(lambda t, x: A.replicator_rhs(x, norm, 3.0, 0.03, 0.03), (0.0, 40.0), x0, t_eval=times, rtol=1e-10, atol=1e-12)
        assert np.max(np.abs(sol.y.T - traj)) < 1e-5, norm


def test_invasion_fitness_equals_a_direct_two_strategy_payoff_difference():
    for norm in C.NORM_KEYS:
        eps = 1e-6
        shares = {"ALLC": eps, "ALLD": 0.0, "DISC": 1 - eps}
        f = A.payoffs(shares, norm, 3.0, 0.03, 0.03)["f"]
        assert A.invasion_fitness("DISC", "ALLC", norm, 3.0, 0.03, 0.03, eps=eps) == pytest.approx(f["ALLC"] - f["DISC"], abs=1e-12)
