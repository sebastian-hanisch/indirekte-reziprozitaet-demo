"""Jede Zahl aus README und App wird hier über die echten Auswertungsfunktionen nachgerechnet (DEMO-PLAYBOOK §4)."""

import pytest

import ire_algorithm as A
import ire_constants as C
import ire_evaluation as E


def table(b=3.0, e=0.02):
    return {r["norm"]: r for r in E.stability_table(b, e, e)}


def test_stability_table_at_two_percent_errors():
    t = table()
    assert t["SJ"]["g"] == pytest.approx(0.962, abs=0.001) and t["SJ"]["f"] == pytest.approx(1.885, abs=0.001)
    assert t["SJ"]["allc"] == pytest.approx(-0.144, abs=0.001) and t["SJ"]["alld"] == pytest.approx(-1.717, abs=0.001)
    assert t["SS"]["g"] == pytest.approx(0.962, abs=0.001) and t["SS"]["allc"] == pytest.approx(-0.038, abs=0.001)
    assert t["IS"]["g"] == pytest.approx(0.338, abs=0.001) and t["IS"]["f"] == pytest.approx(0.662, abs=0.001)
    assert t["IS"]["allc"] == pytest.approx(1.183, abs=0.001) and t["IS"]["alld"] == pytest.approx(-0.603, abs=0.001)
    assert t["SH"]["g"] == pytest.approx(0.338, abs=0.001) and t["SH"]["allc"] == pytest.approx(-0.649, abs=0.001)


def test_only_image_scoring_is_unstable_against_always_help():
    t = table()
    unstable = [k for k, r in t.items() if r["allc"] >= -1e-9 or r["alld"] >= -1e-9]
    assert unstable == ["IS"]


def test_without_errors_two_norms_are_undetermined_and_always_help_is_neutral_elsewhere():
    t = {r["norm"]: r for r in E.stability_table(3.0, 0.0, 0.0)}
    assert not t["IS"]["determined"] and not t["SH"]["determined"]
    assert t["SJ"]["g"] == pytest.approx(1.0) and t["SJ"]["allc"] == pytest.approx(0.0, abs=1e-6)
    assert t["SS"]["allc"] == pytest.approx(0.0, abs=1e-6)


def test_ten_percent_errors():
    t = table(3.0, 0.10)
    assert t["SJ"]["g"] == pytest.approx(0.833, abs=0.001) and t["SJ"]["f"] == pytest.approx(1.500, abs=0.001)
    assert t["SJ"]["allc"] == pytest.approx(-0.474, abs=0.001)


def test_reputation_collapse_under_image_scoring_with_execution_errors_only():
    assert A.reputations(A.monomorphic("DISC"), "IS", 0.02, 0.0)[0] == pytest.approx(0.0, abs=1e-12)


def test_dynamics_end_states():
    def end(norm, e, start):
        return E.analyse(E.Settings(norm, 3.0, e, e, *start))

    assert end("SJ", 0.02, (0.05, 0.05)).winner == "DISC"
    assert end("SS", 0.02, (0.3, 0.1)).final[2] > 0.99
    im = end("IS", 0.02, (0.05, 0.05))
    assert im.final[0] == pytest.approx(0.645, abs=0.01) and im.final[2] == pytest.approx(0.355, abs=0.01) and im.final[1] < 0.01
    assert end("SJ", 0.10, (0.1, 0.5)).winner == "ALLD"                         # zu viele Nie-Helfer am Anfang kippen die Population
    assert end("IS", 0.10, (0.1, 0.5)).winner == "ALLD"


def test_verdicts():
    stable = E.Settings("SJ")
    assert E.verdict(E.analyse(stable), stable)[0] == "success"
    unstable = E.Settings("IS")
    level, text = E.verdict(E.analyse(unstable), unstable)
    assert level == "warning" and "nicht stabil" in text and "Immer-helfen" in text
    undetermined = E.Settings("IS", 3.0, 0.0, 0.0)
    level, text = E.verdict(E.analyse(undetermined), undetermined)
    assert level == "warning" and "unbestimmt" in text


def test_reputation_vs_error_curves():
    g = {}
    for key in C.NORM_KEYS:
        g[key] = [A.payoffs(A.monomorphic("DISC"), key, 3.0, e, e)["g"] for e in (0.01, 0.05, 0.1)]
    assert g["SJ"][0] > 0.9 and g["SJ"] == sorted(g["SJ"], reverse=True)
    assert all(0.30 < v < 0.40 for v in g["IS"]) and all(0.30 < v < 0.40 for v in g["SH"])


def test_trajectory_start_points_are_inside_the_simplex():
    pts = E.start_points()
    assert pts and all(x > 0 and y > 0 and x + y < 0.95 for x, y in pts)
    trajs = E.trajectories(E.Settings("SJ"))
    assert len(trajs) == len(pts) and all(abs(sum(t["end"]) - 1.0) < 1e-9 for t in trajs)


def test_the_sign_of_the_always_help_advantage_depends_on_the_norm_not_on_b_over_c():
    for norm, positive in (("IS", True), ("SJ", False), ("SS", False), ("SH", False)):
        for b in (1.2, 1.5, 2.0, 3.0, 6.0, 10.0):
            v = A.invasion_fitness("DISC", "ALLC", norm, b, 0.02, 0.02)
            assert (v > 0) == positive, (norm, b, v)
            assert A.invasion_fitness("DISC", "ALLD", norm, b, 0.02, 0.02) < 0, (norm, b)
    # Simple Standing und Shunning: die Größe ist sogar von b unabhängig (gleicher Ruf wie Diskriminierer, nur die Kosten unterscheiden sich)
    assert A.invasion_fitness("DISC", "ALLC", "SS", 1.2, 0.02, 0.02) == pytest.approx(A.invasion_fitness("DISC", "ALLC", "SS", 10.0, 0.02, 0.02), abs=1e-6)
