import matplotlib.pyplot as plt
import seaborn as sns

from . import categorical_palette, POSITION_LABELS, TEXT_MUTED, ACCENT


def plot_budget_top5(abordables, budget):
    """Barres horizontales : parmi les joueurs recrutables avec ce budget, quelles sont les
    5 recrues qui en consomment le plus (les plus chères encore accessibles) ? Ne s'appuie
    que sur nom / poste / valeur estimée -> reste synchronisé avec le tableau au-dessus, qui
    se recalcule à chaque changement de budget ou de filtres."""
    top5 = abordables.nlargest(min(5, len(abordables)), "ValeurEstimee")
    order = top5["Name"].tolist()
    palette = categorical_palette(top5["Position"])

    fig, ax = plt.subplots(figsize=(7, 0.6 * len(top5) + 1.5))
    sns.barplot(
        data=top5, x="ValeurEstimee", y="Name", order=order,
        hue="Position", palette=palette, dodge=False, legend=False, ax=ax,
    )
    x_max = max(budget, top5["ValeurEstimee"].max()) * 1.15
    for i, name in enumerate(order):
        row = top5[top5["Name"] == name].iloc[0]
        poste_label = POSITION_LABELS.get(row["Position"], row["Position"])
        ax.text(
            row["ValeurEstimee"] + x_max * 0.015, i, poste_label,
            va="center", color=TEXT_MUTED, fontsize=9,
        )
    ax.axvline(budget, color=ACCENT, linestyle="--", linewidth=2, label=f"Budget = {budget:.1f} M€")
    ax.set_xlim(0, x_max)
    ax.set_title("Les recrues les plus chères encore accessibles avec ce budget")
    ax.set_xlabel("Valeur estimée (M€)")
    ax.set_ylabel("")
    ax.legend(frameon=False, labelcolor=TEXT_MUTED, loc="lower right")
    sns.despine(fig)
    fig.tight_layout()

    why = (
        "Un barplot horizontal classe les joueurs recrutables les plus proches du plafond "
        "budgétaire : il montre qui consomme le plus de budget parmi les recrues possibles, "
        "sans dépendre de l'OVR — seulement nom, poste et valeur estimée."
    )
    top_name, top_value = order[0], float(top5.iloc[0]["ValeurEstimee"])
    interpretation = (
        f"{top_name} est la recrue la plus chère encore accessible avec ce budget "
        f"({top_value:.1f} M€ sur {budget:.1f} M€ disponibles)."
    )
    return fig, why, interpretation
