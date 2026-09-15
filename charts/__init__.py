import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

MAX_CATEGORIES = 6

# Palette fixe (catégorielle, ordre non-cyclé) + rampe séquentielle pour les magnitudes.
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]  # blue, orange, aqua, yellow, magenta
OTHER_COLOR = "#898781"  # gris neutre réservé au groupe "Autres"
ACCENT = "#eb6834"  # même hex que CATEGORICAL[1], utilisé pour une 2e série séquentielle (ex: moyenne)

SEQUENTIAL_BLUE = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]  # step 250 -> 650, clair = faible

POSITION_LABELS = {
    "GK": "Gardien", "CB": "Défenseur central", "LB": "Latéral gauche", "RB": "Latéral droit",
    "CDM": "Milieu défensif", "CM": "Milieu central", "CAM": "Milieu offensif",
    "LM": "Milieu gauche", "RM": "Milieu droit", "LW": "Ailier gauche", "RW": "Ailier droit",
    "ST": "Attaquant",
}

TEXT_PRIMARY = "#0b0b0b"
TEXT_MUTED = "#898781"
GRID_COLOR = "#e1e0d9"
SURFACE = "#fcfcfb"


def apply_style():
    sns.set_theme(style="whitegrid", rc={
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": GRID_COLOR,
        "axes.labelcolor": TEXT_PRIMARY,
        "axes.titlecolor": TEXT_PRIMARY,
        "grid.color": GRID_COLOR,
        "text.color": TEXT_PRIMARY,
        "xtick.color": TEXT_MUTED,
        "ytick.color": TEXT_MUTED,
        "font.family": "sans-serif",
        "axes.titleweight": "bold",
        "axes.titlesize": 12,
    })


apply_style()


def cap_categories(series, max_categories=MAX_CATEGORIES, other_label="Autres"):
    """Regroupe les catégories les moins fréquentes sous 'Autres' pour ne jamais dépasser
    max_categories couleurs distinctes sur un graphique (honnêteté visuelle)."""
    top = series.value_counts().index[: max_categories - 1]
    return series.where(series.isin(top), other_label)


def categorical_palette(series, other_label="Autres"):
    """Associe à chaque catégorie (hors 'Autres') une couleur fixe de la palette, dans
    l'ordre de fréquence décroissante. 'Autres' reste toujours gris, jamais une teinte
    catégorielle, pour ne pas se confondre avec un vrai championnat."""
    order = [c for c in series.value_counts().index if c != other_label]
    palette = {cat: CATEGORICAL[i % len(CATEGORICAL)] for i, cat in enumerate(order)}
    if other_label in series.unique():
        palette[other_label] = OTHER_COLOR
    return palette


def nice_limits(values, pad_frac=0.1, min_span=15, domain=(0, 100)):
    """Bornes d'axe qui zooment sur la plage réellement présente dans les données affichées
    (+ marge), au lieu d'un 0-100 fixe qui écrase la variation quand la sélection est un
    sous-groupe homogène. `min_span` évite à l'inverse de sur-zoomer sur un écart bruité
    quand la sélection est très petite ou très homogène. Toujours borné au domaine théorique
    de l'attribut (0-100 par défaut)."""
    values = np.asarray(values, dtype=float)
    lo, hi = float(values.min()), float(values.max())
    span = max(hi - lo, min_span)
    pad = span * pad_frac
    lo, hi = lo - pad, hi + pad
    return max(lo, domain[0]), min(hi, domain[1])


def ordinal_ramp(n):
    """n couleurs séquentielles (clair = valeur basse, foncé = valeur haute), pour
    encoder un classement (magnitude), jamais une identité catégorielle."""
    if n <= 1:
        return [SEQUENTIAL_BLUE[-1]]
    idx = [round(i * (len(SEQUENTIAL_BLUE) - 1) / (n - 1)) for i in range(n)]
    return [SEQUENTIAL_BLUE[i] for i in idx]
