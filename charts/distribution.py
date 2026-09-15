import matplotlib.pyplot as plt
import seaborn as sns

from . import CATEGORICAL, ACCENT, TEXT_PRIMARY, TEXT_MUTED, nice_limits


def plot_distribution(sel):
    """Histogramme : comment se répartit la note globale (OVR) dans la sélection ?
    Variable unique et quantitative -> l'histogramme est le choix adapté. La courbe de
    densité (KDE) est superposée pour lisser la forme de la distribution ; seaborn la met
    automatiquement à l'échelle du nombre de joueurs (stat="count" par défaut), donc les
    deux restent comparables sur le même axe."""
    mean = sel["OVR"].mean()
    median = sel["OVR"].median()

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(
        sel, x="OVR", binwidth=2, color=CATEGORICAL[0], edgecolor="white", ax=ax,
        kde=True, line_kws=dict(color=TEXT_PRIMARY, linewidth=2, label="Densité (KDE)"),
    )
    ax.axvline(mean, color=ACCENT, linestyle="--", linewidth=2, label=f"Moyenne = {mean:.1f}")
    _, xmax = nice_limits(sel["OVR"], pad_frac=0.15, min_span=8)
    ax.set_xlim(sel["OVR"].min(), xmax)
    ax.set_ylim(bottom=0)
    ax.set_title(f"La note globale se concentre autour de {median:.0f} chez les joueurs sélectionnés")
    ax.set_xlabel("Note globale (OVR, 0-99)")
    ax.set_ylabel("Nombre de joueurs")
    ax.legend(frameon=False, labelcolor=TEXT_MUTED)
    sns.despine(fig)
    fig.tight_layout()

    why = "Un histogramme répond à « comment se répartit une variable quantitative unique ? » — ici la note globale de la sélection. La courbe de densité (KDE) superposée lisse la forme générale de la distribution au-delà du découpage en barres."
    interpretation = f"La moitié des joueurs sélectionnés ont un OVR ≥ {median:.0f}, pour une moyenne de {mean:.1f}."
    return fig, why, interpretation
