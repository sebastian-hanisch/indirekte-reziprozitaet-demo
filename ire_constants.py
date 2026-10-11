"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# Spenderspiel: ein Spender kann einem zufällig getroffenen Empfänger helfen (Kosten C, Nutzen B für den Empfänger). Jede Woche trifft jeder einen anderen.
COST = 1.0
B_MIN, B_MAX, DEFAULT_B, B_STEP = 1.5, 10.0, 3.0, 0.5
E1_MIN, E1_MAX, DEFAULT_E1, E_STEP = 0.0, 0.20, 0.02, 0.01
E2_MIN, E2_MAX, DEFAULT_E2 = 0.0, 0.20, 0.02
SHARE_MIN, SHARE_MAX, SHARE_STEP = 0.0, 0.45, 0.01
DEFAULT_ALLC, DEFAULT_ALLD = 0.05, 0.05          # Anfangsanteile; der Rest sind Diskriminierer
TIME_MAX, DT, RECORD_EVERY = 150.0, 0.1, 10

STRATEGY_KEYS = ("ALLC", "ALLD", "DISC")
STRATEGY_LABELS = {"ALLC": "Immer helfen", "ALLD": "Nie helfen", "DISC": "Diskriminierer"}

# Bewertungsregeln (zweiter Ordnung): wer gilt danach als gut? Reihenfolge: (hilft, Empfänger gut), (hilft, Empfänger schlecht), (hilft nicht, gut), (hilft nicht, schlecht).
NORM_KEYS = ("SJ", "SS", "IS", "SH")
NORMS = {
    "IS": {"label": "Image Scoring", "rule": (1, 1, 0, 0), "description": "Wer hilft, gilt als gut; wer nicht hilft, als schlecht, egal gegenüber wem."},
    "SJ": {"label": "Stern Judging", "rule": (1, 0, 0, 1),
           "description": "Wer einem Guten hilft oder einem Schlechten nicht hilft, gilt als gut; sonst als schlecht."},
    "SS": {"label": "Simple Standing", "rule": (1, 1, 0, 1),
           "description": "Nur wer einem Guten nicht hilft, gilt als schlecht. Einem Schlechten nicht zu helfen ist gerechtfertigt."},
    "SH": {"label": "Shunning", "rule": (1, 0, 0, 0), "description": "Nur wer einem Guten hilft, gilt als gut; alles andere macht schlecht."},
}
DEFAULT_NORM = "SJ"

B_GRID = (1.2, 1.5, 2, 3, 4, 6, 8, 10)
E_GRID = (0.0, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2)
TOL = 1e-9

COLORS = {"ALLC": "#9aa5b1", "ALLD": "#B5483A", "DISC": "#2F6B65"}

PRESETS = {
    "Stern Judging, wenige Fehler": {"norm": "SJ", "b": 3.0, "e1": 0.02, "e2": 0.02, "allc": 0.05, "alld": 0.05},
    "Simple Standing, wenige Fehler": {"norm": "SS", "b": 3.0, "e1": 0.02, "e2": 0.02, "allc": 0.05, "alld": 0.05},
    "Image Scoring, wenige Fehler": {"norm": "IS", "b": 3.0, "e1": 0.02, "e2": 0.02, "allc": 0.05, "alld": 0.05},
    "Shunning, wenige Fehler": {"norm": "SH", "b": 3.0, "e1": 0.02, "e2": 0.02, "allc": 0.05, "alld": 0.05},
    "Stern Judging, viele Fehler (10 %)": {"norm": "SJ", "b": 3.0, "e1": 0.10, "e2": 0.10, "allc": 0.05, "alld": 0.05},
}
PRESET_HELP = {
    "Stern Judging, wenige Fehler": "Die Reputation hält die Kooperation zusammen: Diskriminierer setzen sich durch, Immer-helfen wird nicht belohnt, Nie-helfen stirbt aus.",
    "Simple Standing, wenige Fehler": "Fast dasselbe Ergebnis; Immer-helfen ist hier nur ein wenig im Nachteil, also schwächer unter Druck.",
    "Image Scoring, wenige Fehler": "Der Klassiker: wer einem Schlechten nicht hilft, wird selbst schlecht. Das zerstört die Reputation, und Immer-helfen verdrängt die Diskriminierer.",
    "Shunning, wenige Fehler": "Streng, aber stabil: kaum jemand gilt als gut, entsprechend wenig Kooperation.",
    "Stern Judging, viele Fehler (10 %)": "Mit vielen Fehlern sinkt die gute Reputation; die Kooperation hält, wird aber teurer.",
}
