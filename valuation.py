import numpy as np

# Le dataset ne contient aucune donnée de marché réelle (pas de "playerelo", pas de valeur
# transfert) : uniquement des notes de jeu vidéo (OVR, PAC...) et des infos joueur. La valeur
# ci-dessous est donc une ESTIMATION indicative, pas une vraie évaluation de marché.
#
# Formule : une base exponentielle par OVR (calée sur des repères usuels — un joueur ~91
# vaut plusieurs dizaines de fois plus qu'un ~65), modulée par deux primes de marché connues :
# l'âge (jeunesse/potentiel de revente) et le poste (les attaquants se négocient plus cher
# que les défenseurs/gardiens à OVR égal).
BASE_OVR_REF = 91
BASE_VALUE_REF = 180.0  # M€, valeur repère pour un OVR 91 en pleine forme d'âge, poste neutre
OVR_GROWTH = 0.2126  # +1 point d'OVR ≈ +24% de valeur

AGE_BREAKPOINTS = [(21, 1.30), (24, 1.15), (27, 1.00), (30, 0.85), (33, 0.55), (200, 0.30)]

POSITION_FACTORS = {
    "GK": 0.75,
    "CB": 0.90, "LB": 0.90, "RB": 0.90,
    "CDM": 0.95, "CM": 1.00, "CAM": 1.10,
    "LM": 1.05, "RM": 1.05,
    "LW": 1.15, "RW": 1.15, "ST": 1.15,
}


def _age_factor(age):
    for max_age, factor in AGE_BREAKPOINTS:
        if age <= max_age:
            return factor
    return AGE_BREAKPOINTS[-1][1]


def estimate_value(ovr, age, position):
    """Valeur marchande estimée (en M€) à partir de l'OVR, l'âge et le poste. Indicative
    uniquement — voir le commentaire en tête de module."""
    base = BASE_VALUE_REF * np.exp(OVR_GROWTH * (ovr - BASE_OVR_REF))
    factor = _age_factor(age) * POSITION_FACTORS.get(position, 1.0)
    return round(float(base * factor), 2)


def add_estimated_value(df):
    df = df.copy()
    df["ValeurEstimee"] = [
        estimate_value(ovr, age, pos)
        for ovr, age, pos in zip(df["OVR"], df["Age"], df["Position"])
    ]
    return df


def format_value(value_millions):
    """Formate une valeur en M€ en choisissant l'unité la plus lisible (k€ en dessous de 1 M€)."""
    if value_millions >= 1:
        return f"{value_millions:.1f} M€"
    return f"{value_millions * 1000:.0f} k€"
