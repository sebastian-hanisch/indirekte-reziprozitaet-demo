# Indirekte Reziprozität: Reputation statt Gedächtnis – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-indirekte-reziprozitaet-demo.streamlit.app/)**

Achtes Stück der **Wiederholte-Spiele-Linie** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“.
Nachfolger von [replikator-demo](https://sebastianhanisch-replikator-demo.streamlit.app/) und [tit-for-tat-demo](https://sebastianhanisch-tit-for-tat-demo.streamlit.app/): dort
trafen sich dieselben Partner wieder, hier **wechseln die Partner**, und Kooperation gelingt nur über eine öffentliche **Reputation**. Die Kante ist ein `fix`: direkte Reziprozität
braucht Wiederbegegnung, die indirekte nicht.

Vehikel: Spediteure und Subunternehmer auf einer Frachtbörse; jede Woche trifft jeder einen zufälligen anderen und kann ihm helfen (Kosten 1, Nutzen b). Eigennutz und Imitation sind
Modellannahmen.

## Warum dieses Problem

Wer einem Fremden hilft, der nie zurückhilft, braucht einen Dritten, der das sieht und danach hilft. Das gelingt nur, wenn es eine Regel gibt, **wer als gut gilt**. Die naheliegende
Regel (wer hilft, ist gut) zerstört sich selbst, sobald Fehler passieren. Die Demo rechnet das exakt in einer großen Population und zeigt, welche Regeln stabil sind.

## Modell

Drei Strategien: Immer helfen, Nie helfen, Diskriminierer (hilft nur Empfängern mit gutem Ruf). Vier Bewertungsregeln zweiter Ordnung: Image Scoring, Stern Judging, Simple Standing,
Shunning. Öffentliche Bewertung, Ausführungsfehler e1 und Bewertungsfehler e2. Die stationäre Reputation je Strategie ist eine **affine Gleichung** in g und exakt lösbar; daraus
folgen Auszahlungen, der Invasionsvorteil seltener Strategien und die Replikatordynamik.

## Methodik

- **Reputation:** `reputations`: g = A/(1 − B) aus der affinen Gleichung; unbestimmt (Fehlermeldung), wenn B = 1.
- **Auszahlung:** `payoffs`: b · (erhaltene Hilfe) − c · (geleistete Hilfe).
- **Stabilität:** `invasion_fitness`: Vorteil eines seltenen Eindringlings gegenüber der residenten Strategie.
- **Dynamik:** `integrate`: Replikatordynamik auf dem Simplex (Runge-Kutta 4. Ordnung).

## Befunde (gemessen, keine Behauptungen)

b/c = 3, e1 = e2 = 0,02, reine Diskriminierer-Population.

| Regel | guter Ruf | Auszahlung | Vorteil Immer helfen | Vorteil Nie helfen | Befund |
|---|---|---|---|---|---|
| Stern Judging | 96,2 % | 1,885 | −0,144 | −1,717 | stabil |
| Simple Standing | 96,2 % | 1,885 | −0,038 | −1,717 | stabil, Immer helfen fast neutral |
| Image Scoring | 33,8 % | 0,662 | **+1,183** | −0,603 | **instabil**, guter Ruf bricht ein |
| Shunning | 33,8 % | 0,662 | −0,649 | −0,603 | stabil, aber kaum Kooperation |

Test: `test_stability_table_at_two_percent_errors`, `test_only_image_scoring_is_unstable_against_always_help`.

| Frage | Befund | Test |
|---|---|---|
| Was passiert ohne Fehler? | Bei Image Scoring und Shunning ist die Reputation **unbestimmt**: jedes g ist stationär. Stern Judging und Standing: g = 1, Immer helfen ein neutraler Eindringling (Vorteil 0). | `test_without_errors_two_norms_are_undetermined_and_always_help_is_neutral_elsewhere` |
| Image Scoring nur mit Ausführungsfehlern? | Der gute Ruf bricht auf **null** zusammen: ein Diskriminierer, dessen Hilfe misslingt, gilt als schlecht und bekommt nie wieder Hilfe. | `test_reputation_collapse_under_image_scoring_with_execution_errors_only` |
| Zehn Prozent Fehler? | Stern Judging: guter Ruf 83,3 %, Auszahlung 1,50, Immer helfen −0,474. | `test_ten_percent_errors` |
| Wo enden die Dynamiken (b/c = 3)? | Stern Judging mit 2 % Fehlern aus (5 % Immer helfen, 5 % Nie helfen): 100 % Diskriminierer. Image Scoring: Mischzustand, 64,5 % Immer helfen und 35,5 % Diskriminierer. Mit 10 % Fehlern und 50 % Nie helfen am Anfang kippt auch Stern Judging zu Nie helfen. | `test_dynamics_end_states` |
| Hängt die Stabilität am Nutzen b/c? | Nein, das **Vorzeichen** des Vorteils von Immer helfen hängt nur an der Regel (Image Scoring für jedes b/c positiv, die anderen negativ); Nie helfen verliert bei jedem b/c über 1. | `test_the_sign_of_the_always_help_advantage_depends_on_the_norm_not_on_b_over_c` |

### Befunde gegenüber dem Plan

Der Plan erwartete „Image Scoring instabil, Leading Eight stabil bei öffentlicher Bewertung“. Das bestätigt sich für die zwei Regeln zweiter Ordnung, die hier enthalten sind (Stern
Judging, Simple Standing); die acht „Leading Eight“ im strengen Sinn brauchen Regeln dritter Ordnung (Bewertung hängt auch vom Ruf des Spenders ab) und sind nicht enthalten. Zusätzlich
zeigt die Rechnung: Shunning ist **stabil**, aber mit nur 34 % gutem Ruf und 0,66 Punkten ein schlechtes Gleichgewicht; Stabilität ist also nicht dasselbe wie Wohlfahrt. Und bei
vielen Fehlern (10 %) reicht ein hoher Anfangsanteil von Nie helfen (50 %), um Stern Judging und Image Scoring zu kippen (gemessen; bei Shunning endet derselbe Start bei Diskriminierern): Stabilität gegen **seltene** Eindringlinge ist keine globale Aussage.

## Ehrliche Grenzen

- **Öffentliche Bewertung:** alle teilen dieselbe Reputation. Bei privater Bewertung ist Stabilität deutlich schwerer; hier nicht gerechnet.
- **Unendliche, durchmischte Population:** Drift in kleinen Populationen und Netzwerke ändern die Ergebnisse.
- **Nur Regeln zweiter Ordnung, drei Strategien:** die Leading Eight (dritter Ordnung) sind nicht enthalten.
- **Gleichverteilte, unabhängige Fehler**, Imitation nach Auszahlung als einzige Lernregel.
- **Literatur nur über Zusammenfassungen gelesen.**

## Verifikation

- **Kern:** je Einheit eine Handrechnung (Reputation je Regel und Strategie, mit und ohne Fehler, Auszahlungen, Invasionsvorteile, Replikatordynamik).
- **Orakel** (`tests/test_oracle_indirekte_reziprozitaet.py`): (1) eine **agentenbasierte Simulation** einer Population von 6000 Spielern über 160 Runden gegen die exakte Reputation je
  Strategie und die Auszahlung, für alle vier Regeln; (2) die Reputation als Fixpunkt gegen die Iteration g ← F(g); (3) die Replikatordynamik gegen `scipy.integrate.solve_ivp`.
- **Claims:** jede Zahl dieses READMEs in `tests/test_claims.py`.
- **Oberfläche:** AppTest (jeder Button, jeder Regler am Minimum und Maximum, Permalink begrenzt und rastet ein, Strategien und Regeln erklärt, Fall ohne Fehler warnt) und Footer-Test.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `ire_algorithm.py` | Kern: Reputation, Auszahlung, Invasionsvorteil, Replikatordynamik |
| `ire_constants.py` | Regler-Grenzen, Regeln, Farben, Presets |
| `ire_evaluation.py` | Analyse, Stabilitätstabelle, Trajektorien, Verdikt |
| `ire_presets.py` | Permalink (Begrenzen und Einrasten), Presets |
| `ire_visualization.py` | Plotly-Abbildungen (Simplex, Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy (nur Orakel) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handrechnung, Orakel, Claims, Presets, AppTest-Smoke-Test, Footer |

## Bewusst nicht umgesetzt

- **Private Bewertung (jeder hat eine eigene Meinung):** eigenes Modell, deutlich aufwendiger.
- **Leading Eight im strengen Sinn (dritte Ordnung):** eigener Regelraum.
- **Endliche Populationen und Netzwerke:** siehe replikator-demo für die endliche Population.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
