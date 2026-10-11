"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import ire_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=380, legend=True):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="rgba(0,0,0,0)", showlegend=legend,
                      legend=dict(orientation="h", y=-0.25))
    return lock_axes(fig)


def build_ternary(trajs, current=None):
    """Simplex der drei Strategien: Pfade der Replikatordynamik aus mehreren Startpunkten; die Ecken sind reine Populationen."""
    fig = go.Figure()
    for t in trajs:
        p = t["path"]
        fig.add_trace(go.Scatterternary(a=[v[2] for v in p], b=[v[0] for v in p], c=[v[1] for v in p], mode="lines", line=dict(color="rgba(80,80,80,0.5)", width=1.5),
                                        showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatterternary(a=[p[-1][2]], b=[p[-1][0]], c=[p[-1][1]], mode="markers", marker=dict(size=9, color="rgba(60,60,60,0.9)"),
                                        showlegend=False, hovertemplate="Endzustand: Diskriminierer %{a:.2f}, Immer helfen %{b:.2f}, Nie helfen %{c:.2f}<extra></extra>"))
    if current is not None:
        p = current
        fig.add_trace(go.Scatterternary(a=[v[2] for v in p], b=[v[0] for v in p], c=[v[1] for v in p], mode="lines", name="gewählter Start",
                                        line=dict(color="#e08a2c", width=4)))
        fig.add_trace(go.Scatterternary(a=[p[0][2]], b=[p[0][0]], c=[p[0][1]], mode="markers", name="Start", marker=dict(size=12, color="#e08a2c", symbol="circle-open")))
    fig.update_layout(ternary=dict(sum=1, aaxis=dict(title="Diskriminierer", min=0), baxis=dict(title="Immer helfen", min=0), caxis=dict(title="Nie helfen", min=0)))
    return _base(fig, height=520)


def build_reputation_vs_error(curves):
    fig = go.Figure()
    for key, c in curves.items():
        fig.add_trace(go.Scatter(x=c["e"], y=c["g"], mode="lines+markers", name=C.NORMS[key]["label"], line=dict(width=3),
                                 hovertemplate=C.NORMS[key]["label"] + ": Fehler %{x:.2f}, guter Ruf %{y:.2f}<extra></extra>"))
    fig.update_xaxes(title_text="Fehlerrate (Ausführung und Bewertung je gleich hoch)")
    fig.update_yaxes(title_text="Anteil guter Spieler in der reinen Diskriminierer-Population", range=[0, 1.02])
    return _base(fig, height=360)


def build_invasion_vs_b(curves, norm_label):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curves["b"], y=curves["allc"], mode="lines+markers", name="Immer helfen dringt ein", line=dict(color=C.COLORS["ALLC"], width=3),
                             hovertemplate="b/c = %{x}: %{y:.3f}<extra>Immer helfen</extra>"))
    fig.add_trace(go.Scatter(x=curves["b"], y=curves["alld"], mode="lines+markers", name="Nie helfen dringt ein", line=dict(color=C.COLORS["ALLD"], width=3),
                             hovertemplate="b/c = %{x}: %{y:.3f}<extra>Nie helfen</extra>"))
    fig.add_hline(y=0.0, line=dict(color="rgba(60,60,60,0.8)", width=1.5), annotation_text="darüber: Eindringling gewinnt", annotation_position="top left")
    fig.update_xaxes(title_text=f"Nutzen/Kosten b/c ({norm_label})")
    fig.update_yaxes(title_text="Vorteil des seltenen Eindringlings je Runde")
    return _base(fig, height=360)
