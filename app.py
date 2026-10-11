"""Indirekte Reziprozität: Reputation statt Gedächtnis - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Achtes Stück der Wiederholte-Spiele-Linie: Wechselnde Partner, öffentlich bekannte Reputation. Welche Bewertungsregel hält Kooperation zusammen? Image Scoring gegen
Stern Judging und Simple Standing, exakt gerechnet in einer großen Population.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import ire_algorithm as A
import ire_constants as C
import ire_evaluation as E
from ire_evaluation import Settings, fmt
from ire_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from ire_visualization import build_invasion_vs_b, build_reputation_vs_error, build_ternary

st.set_page_config(page_title="Indirekte Reziprozität: Reputation statt Gedächtnis – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return E.analyse(settings)


@st.cache_data(show_spinner=False)
def _trajectories(settings):
    return E.trajectories(settings)


@st.cache_data(show_spinner=False)
def _stability(b, e1, e2):
    return E.stability_table(b, e1, e2)


st.title("⭐ Indirekte Reziprozität: Reputation statt Gedächtnis")
st.markdown(
    """
Bisher kannten sich die Partner und trafen sich wieder. In einem Markt mit **wechselnden Partnern** (Frachtbörse, Subunternehmer) ist das anders: Ich helfe jemandem,
der mir nie helfen wird, und erwarte, dass ein Dritter mir hilft, weil er sieht, dass ich geholfen habe. Das trägt nur, wenn es eine **Reputation** gibt (gut oder
schlecht) und eine **Regel, wer als gut gilt**. Welche Regel hält Kooperation zusammen? Die Antwort überrascht: die naheliegende (wer hilft, ist gut) zerstört sich
selbst, sobald Fehler passieren.

Diese Demo rechnet das in einer großen Population exakt: stationäre Reputation, Auszahlung je Strategie, Stabilität der Diskriminierer und die Replikatordynamik.

Weiter unten: **❓ Kernfrage**, drei Experimente (**🔬**), **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**. Vorgänger sind
[replikator-demo](https://sebastianhanisch-replikator-demo.streamlit.app/) (welche Strategie hält sich in einer Population) und
[tit-for-tat-demo](https://sebastianhanisch-tit-for-tat-demo.streamlit.app/) (Kooperation durch Wiederbegegnung).
"""
)

with st.expander("So funktioniert indirekte Reziprozität", expanded=True):
    st.markdown(
        """
1. **Jede Woche** trifft jeder Spediteur einen zufälligen anderen. Er kann ihm **helfen** (Kosten c = 1 für ihn, Nutzen b für den anderen) oder nicht.
2. **Alle sehen** die Reputation des Empfängers (gut oder schlecht) und bewerten danach den Spender neu, nach einer festen **Bewertungsregel**.
3. **Fehler:** Mit Wahrscheinlichkeit e1 misslingt eine beabsichtigte Hilfe, mit Wahrscheinlichkeit e2 wird eine Handlung falsch bewertet.
4. **Evolution:** Wer mehr verdient, wird nachgeahmt (Replikatordynamik wie in replikator-demo).
        """
    )

with st.expander("Die drei Strategien und die vier Bewertungsregeln: wer macht was?", expanded=True):
    st.markdown(
        "| Strategie | Verhalten |\n|---|---|\n"
        "| **Immer helfen** | hilft jedem, auch dem mit schlechtem Ruf |\n"
        "| **Nie helfen** | hilft niemandem |\n"
        "| **Diskriminierer** | hilft nur Empfängern mit gutem Ruf |"
    )
    rows = ["| Regel | Bedeutung | hilft einem Guten | hilft einem Schlechten | hilft einem Guten nicht | hilft einem Schlechten nicht |", "|---|---|---|---|---|---|"]
    for key in C.NORM_KEYS:
        n = C.NORMS[key]
        cells = ["gut" if v else "schlecht" for v in n["rule"]]
        rows.append(f"| **{n['label']}** | {n['description']} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    st.markdown("\n".join(rows))
    st.caption("Die vier rechten Spalten zeigen, wie der Spender danach bewertet wird. Der Unterschied liegt in den beiden Fällen, in denen er einem Schlechten gegenübersteht.")

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
cols = st.columns(len(C.PRESETS))
for col, name in zip(cols, C.PRESETS):
    with col:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    st.markdown("**Bewertung**")
    norm = st.selectbox("Bewertungsregel", C.NORM_KEYS, key="norm_select", format_func=lambda k: C.NORMS[k]["label"],
                        help="Wer nach einer Handlung als gut gilt.")
    st.caption(f"**{C.NORMS[norm]['label']}:** {C.NORMS[norm]['description']}")
    st.markdown("**Spiel**")
    b = st.slider("Nutzen b (Kosten c = 1)", *bounds("b_slider"), step=C.B_STEP, key="b_slider", help="Wie viel dem Empfänger die Hilfe bringt, im Verhältnis zu den Kosten.")
    e1 = st.slider("Ausführungsfehler e1", *bounds("e1_slider"), step=C.E_STEP, key="e1_slider", help="Wahrscheinlichkeit, dass eine beabsichtigte Hilfe misslingt.")
    e2 = st.slider("Bewertungsfehler e2", *bounds("e2_slider"), step=C.E_STEP, key="e2_slider", help="Wahrscheinlichkeit, dass eine Handlung falsch bewertet wird.")
    st.markdown("**Anfangsanteile**")
    allc = st.slider("Anteil Immer helfen", *bounds("allc_slider"), step=C.SHARE_STEP, key="allc_slider", help="Der Rest nach Immer helfen und Nie helfen sind Diskriminierer.")
    alld = st.slider("Anteil Nie helfen", *bounds("alld_slider"), step=C.SHARE_STEP, key="alld_slider", help="Anfangsanteil der Nie-Helfer.")

sync_query_params({"norm_select": norm, "b_slider": float(b), "e1_slider": round(float(e1), 2), "e2_slider": round(float(e2), 2),
                   "allc_slider": round(float(allc), 2), "alld_slider": round(float(alld), 2)})

settings = Settings(norm, float(b), round(float(e1), 2), round(float(e2), 2), round(float(allc), 2), round(float(alld), 2))
with st.spinner("Rechne die Dynamik ..."):
    an = _analysis(settings)
    trajs = _trajectories(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown(f"## 🎬 Dynamik bei {C.NORMS[norm]['label']}")
if not an.determined:
    st.warning("Ohne Fehler (e1 = e2 = 0) ist die Reputation bei dieser Regel unbestimmt: jeder Anteil guter Spieler ist stationär. Setzen Sie e1 oder e2 über null.")
else:
    m1, m2, m3, m4 = st.columns(4)
    names = [C.STRATEGY_LABELS[s] for s in C.STRATEGY_KEYS]
    top = max(range(3), key=lambda i: an.final[i])
    m1.metric("Am Ende vorn", names[top], delta=f"{fmt(an.final[top] * 100, 0)} %", delta_color="off")
    m2.metric("Guter Ruf in der reinen Diskriminierer-Population", f"{fmt(an.mono['g'] * 100, 0)} %", delta="stationär", delta_color="off")
    m3.metric("Auszahlung je Runde dort", fmt(an.mono["f"]["DISC"]), delta=f"Maximum b − c = {fmt(settings.b - C.COST)}", delta_color="off")
    m4.metric("Vorteil von Immer helfen / Nie helfen als Eindringling", f"{fmt(an.invasion_allc, 3)} / {fmt(an.invasion_alld, 3)}", delta="negativ = stabil", delta_color="off")
    current = [tuple(row) for row in an.shares]
    st.plotly_chart(build_ternary(trajs, current), width="stretch", key="ternary_chart")
    st.caption("Jeder dünne Pfad ist die Replikatordynamik aus einem anderen Startpunkt, der dicke orange der gewählte (Regler Anfangsanteile). Die Ecken sind reine Populationen.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Hält die Reputation die Kooperation zusammen?")
level, sentence = E.verdict(an, settings)
{"success": st.success, "warning": st.warning, "info": st.info}[level](sentence)
st.markdown("---")

# --- Experiment 1 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Welche Regel ist bei diesen Fehlern stabil?")
st.caption(f"Reine Diskriminierer-Population bei b/c = {fmt(settings.b, 1)}, e1 = {fmt(settings.e1)}, e2 = {fmt(settings.e2)}: guter Ruf, Auszahlung und der Vorteil seltener Eindringlinge.")
table = _stability(settings.b, settings.e1, settings.e2)
rows = ["| Regel | guter Ruf | Auszahlung | Vorteil Immer helfen | Vorteil Nie helfen | stabil? |", "|---|---|---|---|---|---|"]
for r in table:
    if r["determined"]:
        stable = r["allc"] < -C.TOL and r["alld"] < -C.TOL
        rows.append(f"| **{r['label']}** | {fmt(r['g'] * 100, 0)} % | {fmt(r['f'])} | {fmt(r['allc'], 3)} | {fmt(r['alld'], 3)} | {'ja' if stable else 'nein'} |")
    else:
        rows.append(f"| **{r['label']}** | unbestimmt | – | – | – | – |")
st.markdown("\n".join(rows))
stable_names = [r["label"] for r in table if r["determined"] and r["allc"] < -C.TOL and r["alld"] < -C.TOL]
st.info(f"Stabil sind hier: {', '.join(stable_names) or 'keine'}. Bei Image Scoring dringt Immer helfen ein, weil es nie wegen „berechtigter“ Verweigerung abgewertet wird. "
        "Bei Shunning bleibt die Kooperation stabil, aber auf niedrigem Niveau, weil kaum jemand als gut gilt.")
st.markdown("---")

# --- Experiment 2 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie viel Fehler verträgt der Ruf?")
st.caption("Anteil guter Spieler in der reinen Diskriminierer-Population über die Fehlerrate (e1 = e2): je Regel.")
curves = {}
for key in C.NORM_KEYS:
    es, gs = [], []
    for e in C.E_GRID:
        try:
            es.append(e)
            gs.append(A.payoffs(A.monomorphic("DISC"), key, settings.b, e, e)["g"])
        except ValueError:
            es.pop()
    curves[key] = {"e": es, "g": gs}
st.plotly_chart(build_reputation_vs_error(curves), width="stretch", key="rep_chart")
st.info("Stern Judging und Simple Standing halten den guten Ruf bei wenigen Fehlern nahe 100 %. Image Scoring und Shunning fallen schon bei kleinen Fehlern auf rund ein Drittel: "
        "ein einzelner Fehler macht einen Spender schlecht, und Schlechte werden von Diskriminierern nicht bedient, also auch nicht gut gemacht.")
st.markdown("---")

# --- Experiment 3 --------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Wie hoch muss der Nutzen sein?")
st.caption(f"Vorteil eines seltenen Eindringlings gegenüber den Diskriminierern über b/c, bei {C.NORMS[settings.norm]['label']} und den eingestellten Fehlern (nur bei bestimmter Reputation).")
bs, allcs, allds = [], [], []
for bb in C.B_GRID:
    try:
        allcs.append(A.invasion_fitness("DISC", "ALLC", settings.norm, float(bb), settings.e1, settings.e2))
        allds.append(A.invasion_fitness("DISC", "ALLD", settings.norm, float(bb), settings.e1, settings.e2))
        bs.append(bb)
    except ValueError:
        pass
if bs:
    st.plotly_chart(build_invasion_vs_b({"b": bs, "allc": allcs, "alld": allds}, C.NORMS[settings.norm]["label"]), width="stretch", key="inv_chart")
    st.info("Der Vorteil von Nie helfen als Eindringling ist bei jedem b/c über 1 negativ, weil Diskriminierer ihnen die Hilfe verweigern. Das **Vorzeichen** beim Vorteil von "
            "Immer helfen hängt dagegen nur an der Bewertungsregel, nicht an b/c: bei Image Scoring ist er für jedes b/c positiv, bei den anderen drei Regeln negativ. "
            "Mehr Nutzen macht die Regel nicht stabiler, er verstärkt nur das Vorzeichen.")
else:
    st.info("Ohne Fehler ist die Reputation bei dieser Regel unbestimmt; bitte e1 oder e2 über null einstellen.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Öffentliche Bewertung: alle teilen dieselbe Reputation** | Bei privater Bewertung (jeder hat eigene Meinungen) ist die Stabilität deutlich schwerer zu erreichen; Stern Judging verliert dabei besonders. Hier nicht gerechnet. | - |
| **Unendlich große, gut durchmischte Population** | Zufallsdrift in kleinen Populationen und Netzwerkstrukturen ändern die Ergebnisse. | `replikator-demo` (endliche Population) |
| **Nur drei Strategien und vier Regeln zweiter Ordnung** | Dritter Ordnung (Bewertung hängt auch vom Ruf des Spenders ab) gibt es acht stabile Regeln, die „Leading Eight“; hier sind nur die zweiter Ordnung enthalten. | - |
| **Fehler unabhängig und gleich häufig** | Systematische Fehler (ein Plattformfehler trifft viele) verändern die Reputationsdynamik. | - |
| **Imitation nach Auszahlung** | Andere Lernregeln können andere Zustände erreichen. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Reputation.** Jeder Spieler ist gut oder schlecht. Eine Regel $d(a, r) \in \{0,1\}$ bewertet den Spender nach Handlung $a \in \{C, D\}$ gegenüber einem Empfänger
mit Ruf $r \in \{G, B\}$; mit Wahrscheinlichkeit $e_2$ kehrt sich die Bewertung um. Strategie $s$ hilft einem Empfänger mit Ruf $r$ mit Wahrscheinlichkeit $p_s(r)$ (mit
Ausführungsfehler $e_1$: Immer helfen $1 - e_1$, Nie helfen $0$, Diskriminierer $(1 - e_1)\,[r = G]$).

**Stationärer Ruf.** Mit $g$ als Anteil guter Spieler ist $Q_s(g) = g\,q_s(G) + (1-g)\,q_s(B)$ mit $q_s(r) = p_s(r)\,d(C,r) + (1 - p_s(r))\,d(D,r)$, und
$g_s = (1 - e_2)\,Q_s + e_2\,(1 - Q_s)$. Wegen $g = \sum_s x_s g_s$ und der Linearität in $g$ gilt $g = A/(1 - B)$ exakt.

**Auszahlung.** $f_s = b \sum_t x_t\,[\,g_s\,p_t(G) + (1 - g_s)\,p_t(B)\,] - c\,[\,g\,p_s(G) + (1-g)\,p_s(B)\,]$.

**Stabilität.** Die reine Diskriminierer-Population ist gegen $s$ stabil, wenn $f_s - f_{\mathrm{DISC}} < 0$ bei seltenem $s$. **Dynamik:** $\dot x_s = x_s\,(f_s - \bar f)$.

**Literatur.** Nowak und Sigmund (1998), *Evolution of indirect reciprocity by image scoring*, Nature 393, 573–577 (Image Scoring); Leimar und Hammerstein (2001), *Evolution of cooperation through indirect reciprocity*, Proceedings of the Royal Society B 268, 745–753 (Zweifel an der Stabilität von Image Scoring); Panchanathan und Boyd (2003), *A tale of two defectors: the importance of standing for evolution of indirect reciprocity*, Journal of Theoretical Biology 224, 115–126 (mit Fehlern trägt Image Scoring nicht, Standing schon); Ohtsuki und Iwasa (2004), *How should we define goodness? Reputation dynamics in indirect reciprocity*, Journal of Theoretical Biology 231, 107–120 (die „Leading Eight“); Pacheco, Santos und Chalub (2006), *Stern-judging: a simple, successful norm which promotes cooperation under indirect reciprocity*, PLoS Computational Biology 2, e178. Nur Zusammenfassungen gelesen. Die Zahlen sind hier gerechnet und gegen eine agentenbasierte Simulation geprüft.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
