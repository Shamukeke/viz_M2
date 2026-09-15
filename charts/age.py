import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from . import CATEGORICAL, ACCENT, TEXT_MUTED, TEXT_PRIMARY, nice_limits

MIN_SAMPLE_PER_AGE = 5


def plot_age_curve(sel):
    """Courbe de forme par âge : à quel âge l'OVR moyen est-il le plus haut dans la
    sélection ? L'âge est quantitatif mais à faible cardinalité (entiers 17-44) -> on
    agrège en OVR moyen par âge (ligne) avec une bande Q1-Q3 pour la dispersion, plutôt
    qu'un nuage de points brut illisible dès que l'effectif grandit. Les points bruts
    restent affichés en fond (rien n'est caché), mais les âges avec moins de
    MIN_SAMPLE_PER_AGE joueurs sont exclus de la ligne/bande : une moyenne sur 1-2
    joueurs n'est pas une tendance fiable."""
    g = sel.groupby("Age")["OVR"]
    stats = pd.DataFrame({
        "mean": g.mean(),
        "count": g.count(),
        "q1": g.quantile(0.25),
        "q3": g.quantile(0.75),
    })
    reliable = stats[stats["count"] >= MIN_SAMPLE_PER_AGE]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    # Léger jitter horizontal sur l'affichage uniquement (l'âge est un entier) pour éviter
    # que les points ne s'empilent en colonnes opaques et masquent la vraie densité.
    rng = np.random.default_rng(0)
    jitter = rng.uniform(-0.18, 0.18, size=len(sel))
    ax.scatter(
        sel["Age"] + jitter, sel["OVR"], s=10, color=TEXT_MUTED, alpha=0.10,
        linewidth=0, zorder=1, label="Joueurs (bruts)",
    )

    peak_age = peak_value = None
    if not reliable.empty:
        ax.fill_between(
            reliable.index, reliable["q1"], reliable["q3"],
            color=CATEGORICAL[0], alpha=0.18, zorder=2, label="Q1-Q3 par âge",
        )
        ax.plot(
            reliable.index, reliable["mean"], color=CATEGORICAL[0], linewidth=2.5,
            marker="o", markersize=5, zorder=3, label="OVR moyen",
        )
        peak_age = reliable["mean"].idxmax()
        peak_value = reliable["mean"].max()
        ax.axvline(peak_age, color=ACCENT, linestyle="--", linewidth=1.5, zorder=2)
        ax.annotate(
            f"Pic à {peak_age} ans (OVR moyen {peak_value:.1f})",
            xy=(peak_age, peak_value), xytext=(10, 12), textcoords="offset points",
            fontsize=9, color=ACCENT, fontweight="bold",
        )

    xmin, xmax = int(sel["Age"].min()), int(sel["Age"].max())
    if xmin == xmax:
        xmin, xmax = xmin - 1, xmax + 1
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(nice_limits(sel["OVR"], pad_frac=0.12, min_span=10))
    title = (
        f"La forme culmine vers {peak_age} ans chez les joueurs sélectionnés"
        if peak_age is not None
        else "Pas assez de joueurs par âge pour dégager une tendance fiable"
    )
    ax.set_title(title, color=TEXT_PRIMARY)
    ax.set_xlabel("Âge")
    ax.set_ylabel("Note globale (OVR, 0-99)")
    # Légende sous le graphique plutôt que dans le cadre : la ligne verticale du pic
    # peut tomber n'importe où selon la sélection et viendrait sinon la traverser.
    ax.legend(
        frameon=False, labelcolor=TEXT_MUTED, loc="upper center",
        bbox_to_anchor=(0.5, -0.14), ncol=3,
    )
    sns.despine(fig)
    fig.tight_layout()

    why = (
        "Une courbe (OVR moyen par âge, avec une bande Q1-Q3) montre la tendance de forme "
        "selon l'âge sans le bruit d'un nuage de points brut à fort effectif — utile pour "
        "repérer les jeunes profils à fort potentiel de revente. Les âges avec moins de "
        f"{MIN_SAMPLE_PER_AGE} joueurs restent visibles en points isolés, mais sont exclus de "
        "la moyenne/bande, peu fiable sur si peu d'observations."
    )
    interpretation = (
        f"L'OVR moyen culmine à {peak_value:.1f} vers {peak_age} ans dans la sélection actuelle."
        if peak_age is not None
        else "La sélection actuelle ne contient pas assez de joueurs par âge pour dégager une tendance fiable."
    )
    return fig, why, interpretation
