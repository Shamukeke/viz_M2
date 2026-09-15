import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from . import cap_categories, categorical_palette, ordinal_ramp, nice_limits, CATEGORICAL, TEXT_MUTED, SURFACE, POSITION_LABELS


def plot_comparaison(sel):
    """Boxplot : le dribble (variable quantitative) diffère-t-il selon le poste (variable
    qualitative) ? Comparer une mesure entre groupes -> boxplot, avec un axe partagé entre
    tous les postes (pour ne pas exagérer les écarts) mais zoomé sur la plage réellement
    présente dans la sélection plutôt que figé à 0-100, sinon un sous-groupe homogène
    écrase toute variation dans une bande minuscule."""
    # Le dribble n'est pas un attribut significatif pour les gardiens dans ce dataset
    # (valeurs artificiellement hautes) : on les exclut pour une comparaison honnête.
    df = sel[sel["Position"] != "GK"].copy()
    if df.empty:
        df = sel.copy()
    df["Position"] = cap_categories(df["Position"])
    order = df.groupby("Position")["DRI"].median().sort_values(ascending=False).index
    ramp = ordinal_ramp(len(order))  # foncé = médiane haute, clair = médiane basse (magnitude)

    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(
        data=df, x="Position", y="DRI", order=order,
        hue="Position", palette=dict(zip(order, ramp)), legend=False, ax=ax,
    )
    ax.set_ylim(nice_limits(df["DRI"], min_span=20))
    top_pos = order[0]
    top_label = POSITION_LABELS.get(top_pos, top_pos)
    ax.set_title(f"Les {top_label.lower()}s ({top_pos}) dribblent mieux que les autres postes")
    ax.set_xlabel("Poste")
    ax.set_ylabel("Dribble (DRI, 0-100)")
    sns.despine(fig)
    fig.tight_layout()

    why = "Un boxplot compare la distribution d'une variable quantitative (le dribble) entre plusieurs groupes (les postes), sur un axe partagé et zoomé sur la plage réellement présente dans la sélection. Les gardiens sont exclus : leur DRI n'est pas un attribut de jeu réel dans ce dataset."
    interpretation = f"Le poste {top_pos} ({top_label}) affiche la médiane de dribble la plus haute de la sélection."
    return fig, why, interpretation


def plot_radar(df, name_a, name_b):
    """Bonus scouting : radar PAC/SHO/PAS/DRI/PHY pour comparer deux joueurs.
    Lisible à 2-3 joueurs seulement ; l'ordre des axes est fixe pour rester comparable."""
    stats = ["PAC", "SHO", "PAS", "DRI", "PHY"]
    labels_fr = ["Vitesse", "Tir", "Passe", "Dribble", "Physique"]
    angles = np.linspace(0, 2 * np.pi, len(stats), endpoint=False).tolist()
    angles += angles[:1]

    # Carrée, comme le diagramme en disque affiché à côté : les deux figures sont
    # étirées à la même largeur de colonne (width="stretch"), donc un même ratio
    # 1:1 et un remplissage similaire du cadre les rendent visuellement symétriques.
    fig, ax = plt.subplots(figsize=(3, 3), subplot_kw=dict(polar=True))
    for key, name, color in (("a", name_a, CATEGORICAL[0]), ("b", name_b, CATEGORICAL[1])):
        row = df.loc[df["Name"] == name, stats].iloc[0].tolist()
        row += row[:1]
        ax.plot(angles, row, color=color, linewidth=1.5, label=name)
        ax.fill(angles, row, color=color, alpha=0.15)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels_fr, fontsize=7)
    ax.set_ylim(0, 100)
    ax.set_title(f"{name_a} vs {name_b}\nsur 5 attributs clés", color="#0b0b0b", fontweight="bold", fontsize=8, pad=12)
    ax.tick_params(colors=TEXT_MUTED, labelsize=6)
    # Légende sous le graphique (au lieu de très à l'extérieur à droite) pour que
    # tout tienne dans le cadre de la figure, sans être coupé ni nécessiter de scroll.
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False, fontsize=7)
    fig.tight_layout(pad=0.3)
    return fig


def plot_position_distribution(sel):
    """Diagramme en disque : comment se répartissent les postes dans la sélection actuelle ?
    Une seule variable qualitative -> un diagramme circulaire montre la part de chaque poste,
    regroupé à 6 catégories max ('Autres' en gris) pour rester lisible, avec les mêmes couleurs
    catégorielles que le reste de l'app."""
    capped = cap_categories(sel["Position"])
    counts = capped.value_counts()
    palette = categorical_palette(capped)
    colors = [palette[pos] for pos in counts.index]
    labels = [POSITION_LABELS.get(pos, pos) for pos in counts.index]

    # Carrée, comme le radar affiché à côté : même ratio 1:1 pour que les deux
    # figures, une fois étirées à la même largeur de colonne, paraissent symétriques.
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.pie(
        counts.values, labels=labels, colors=colors, startangle=90,
        autopct="%1.0f%%", pctdistance=0.75,
        textprops=dict(fontsize=7, color="#0b0b0b"),
        wedgeprops=dict(linewidth=1, edgecolor=SURFACE),
    )
    ax.set_title("Répartition par poste", fontweight="bold", fontsize=8, pad=12)
    fig.tight_layout(pad=0.3)

    top_pos = counts.index[0]
    top_share = counts.iloc[0] / counts.sum() * 100
    if top_pos == "Autres":
        who = 'le groupe "Autres" (postes minoritaires regroupés)'
    else:
        who = f"le poste {POSITION_LABELS.get(top_pos, top_pos)} ({top_pos})"
    why = (
        "Un diagramme en disque montre la part de chaque poste dans la sélection actuelle : "
        "une seule variable qualitative, dont on regarde la répartition en proportions."
    )
    interpretation = f"{who[0].upper()}{who[1:]} représente {top_share:.0f}% de la sélection actuelle."
    return fig, why, interpretation
