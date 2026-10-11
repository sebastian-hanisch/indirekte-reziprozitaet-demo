"""Mini-Instanz-Tests je Einheit (DEMO-PLAYBOOK §1b): von Hand gerechnet, b = 3, c = 1."""

import numpy as np
import pytest

import ire_algorithm as A
import ire_constants as C


def mono(s):
    return A.monomorphic(s)


def test_cooperation_probability():
    assert A.cooperation_probability("ALLC", False, 0.1) == pytest.approx(0.9)
    assert A.cooperation_probability("ALLD", True, 0.1) == 0.0
    assert A.cooperation_probability("DISC", True, 0.1) == pytest.approx(0.9)
    assert A.cooperation_probability("DISC", False, 0.1) == 0.0
    with pytest.raises(ValueError):
        A.cooperation_probability("XYZ", True, 0.0)


def test_reputations_by_hand_without_errors():
    # Nie helfen: Stern Judging bewertet „einem Schlechten nicht helfen“ als gut, „einem Guten nicht helfen“ als schlecht: g = 1 − g → 1/2.
    g, gs = A.reputations(mono("ALLD"), "SJ", 0.0, 0.0)
    assert g == pytest.approx(0.5) and gs["ALLD"] == pytest.approx(0.5)
    # Diskriminierer unter Stern Judging: immer gut. Image Scoring und Nie helfen: immer schlecht.
    assert A.reputations(mono("DISC"), "SJ", 0.0, 0.0)[0] == pytest.approx(1.0)
    assert A.reputations(mono("ALLD"), "IS", 0.0, 0.0)[0] == pytest.approx(0.0)
    assert A.reputations(mono("ALLC"), "IS", 0.0, 0.0)[0] == pytest.approx(1.0)
    # Simple Standing: Nie helfen gilt nur gegenüber einem Guten als schlecht → g = 1 − g · 0 ... : q_G = 0, q_B = 1 → Q = 1 − g → 1/2.
    assert A.reputations(mono("ALLD"), "SS", 0.0, 0.0)[0] == pytest.approx(0.5)


def test_reputation_is_undetermined_where_every_g_is_stationary():
    with pytest.raises(ValueError):
        A.reputations(mono("DISC"), "IS", 0.0, 0.0)          # Diskriminierer unter Image Scoring ohne Fehler
    with pytest.raises(ValueError):
        A.reputations(mono("DISC"), "SH", 0.0, 0.0)
    # Mit Ausführungsfehlern allein ist sie bestimmt, aber null: ein Diskriminierer, dessen Hilfe misslingt, gilt als schlecht, und Schlechte bekommen nie wieder Hilfe.
    assert A.reputations(mono("DISC"), "IS", 0.02, 0.0)[0] == pytest.approx(0.0, abs=1e-12)
    assert 0.0 < A.reputations(mono("DISC"), "IS", 0.02, 0.02)[0] < 0.5          # mit Bewertungsfehlern entsteht ein kleiner Rest guter Spieler


def test_reputation_with_errors_by_hand():
    # Nur Immer-helfen unter Image Scoring: Q = 1 − e1 (hilft mit 1 − e1, sonst nicht); g = (1 − e2) Q + e2 (1 − Q)
    e1, e2 = 0.1, 0.05
    g, _ = A.reputations(mono("ALLC"), "IS", e1, e2)
    q = 1 - e1
    assert g == pytest.approx((1 - e2) * q + e2 * (1 - q))


def test_payoffs_by_hand():
    r = A.payoffs(mono("ALLC"), "IS", 3.0, 0.0, 0.0)
    assert r["f"]["ALLC"] == pytest.approx(3.0 * 1.0 - 1.0 * 1.0)             # bekommt 3, gibt 1
    r = A.payoffs(mono("ALLD"), "IS", 3.0, 0.0, 0.0)
    assert r["f"]["ALLD"] == pytest.approx(0.0)
    r = A.payoffs(mono("DISC"), "SJ", 3.0, 0.0, 0.0)
    assert r["g"] == pytest.approx(1.0) and r["f"]["DISC"] == pytest.approx(2.0)


def test_invasion_fitness_by_hand_without_errors():
    # Stern Judging: Nie helfen bekommt nichts (Ruf schlecht gegenüber Diskriminierern, die nur Guten helfen), gibt nichts: Vorteil 0 − 2.
    assert A.invasion_fitness("DISC", "ALLD", "SJ", 3.0, 0.0, 0.0) == pytest.approx(-2.0, abs=1e-5)
    # Immer helfen ist ohne Fehler ein neutraler Eindringling (gleiche Auszahlung: auch ALLC hat Ruf 1)
    assert A.invasion_fitness("DISC", "ALLC", "SJ", 3.0, 0.0, 0.0) == pytest.approx(0.0, abs=1e-5)


def test_replicator_rhs_conserves_the_total_and_vanishes_at_corners():
    x = np.array([0.2, 0.3, 0.5])
    assert A.replicator_rhs(x, "SJ", 3.0, 0.02, 0.02).sum() == pytest.approx(0.0, abs=1e-12)
    for i in range(3):
        e = np.zeros(3)
        e[i] = 1.0
        assert np.allclose(A.replicator_rhs(e, "SJ", 3.0, 0.02, 0.02), 0.0)


def test_integrate_keeps_the_simplex_and_records_the_end_state():
    times, traj = A.integrate([0.1, 0.1, 0.8], "SJ", 3.0, 0.02, 0.02, t_max=5.0, dt=0.1, record_every=7)
    assert np.allclose(traj.sum(axis=1), 1.0) and (traj >= 0).all()
    assert times[-1] == pytest.approx(5.0)


def test_initial_mix_validates():
    assert A.initial_mix(0.1, 0.2) == pytest.approx([0.1, 0.2, 0.7])
    with pytest.raises(ValueError):
        A.initial_mix(0.7, 0.5)
    with pytest.raises(ValueError):
        A.initial_mix(-0.1, 0.0)
