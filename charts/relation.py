import plotly.express as px

from . import cap_categories, categorical_palette, nice_limits, TEXT_PRIMARY, TEXT_MUTED, GRID_COLOR, SURFACE, ACCENT


def plot_relation(sel):
    """Nuage de points interactif : la vitesse et le dribble sont-ils liés ? Deux variables
    quantitatives -> scatterplot, coloré par championnat (regroupé à 6 catégories max, une
    teinte fixe par championnat, 'Autres' toujours en gris). En Plotly pour une légende
    cliquable : un clic masque/réaffiche un championnat, un double-clic l'isole seul — utile
    pour comparer les championnats un par un sans re-filtrer. Les axes sont zoomés sur la
    plage réellement présente dans la sélection plutôt que figés à 20-100, sinon une
    sélection déjà filtrée sur vitesse/dribble se retasse dans un coin du graphique.
    Deux lignes verticales marquent les quartiles Q1 (25%) et Q3 (75%) de la vitesse."""
    df = sel.copy()
    df["Championnat"] = cap_categories(df["League"])
    palette = categorical_palette(df["Championnat"])
    corr = sel["PAC"].corr(sel["DRI"])

    xlim = nice_limits(sel["PAC"], min_span=20)
    ylim = nice_limits(sel["DRI"], min_span=20)
    q1_pac = sel["PAC"].quantile(0.25)
    q3_pac = sel["PAC"].quantile(0.75)

    fig = px.scatter(
        df, x="PAC", y="DRI", color="Championnat",
        category_orders={"Championnat": list(palette.keys())},
        color_discrete_map=palette,
        hover_name="Name",
        hover_data={"PAC": True, "DRI": True, "Championnat": True},
        opacity=0.85,
    )
    fig.update_traces(marker=dict(size=14, line=dict(width=0.8, color="white")))

    if xlim[0] < 80 < xlim[1] and ylim[0] < 80 < ylim[1]:
        fig.add_shape(
            type="line", x0=80, x1=80, y0=ylim[0], y1=ylim[1],
            line=dict(color=TEXT_MUTED, dash="dot", width=1),
        )
        fig.add_shape(
            type="line", x0=xlim[0], x1=xlim[1], y0=80, y1=80,
            line=dict(color=TEXT_MUTED, dash="dot", width=1),
        )
        fig.add_annotation(
            x=80, y=80, xanchor="left", yanchor="bottom", xshift=4, yshift=4,
            text="zone ailier rapide<br>& bon dribbleur",
            showarrow=False, font=dict(size=11, color=TEXT_MUTED),
        )

    # Repères de dispersion sur la vitesse : quartiles Q1 (25%) et Q3 (75%), pour
    # situer d'un coup d'œil où se trouve le quart le plus lent / le plus rapide.
    fig.add_vline(
        x=q1_pac, line=dict(color=ACCENT, dash="dash", width=1.5),
        annotation_text=f"Q1 (25%) = {q1_pac:.0f}", annotation_position="top",
        annotation_font=dict(color=ACCENT, size=11),
    )
    fig.add_vline(
        x=q3_pac, line=dict(color=ACCENT, dash="dash", width=1.5),
        annotation_text=f"Q3 (75%) = {q3_pac:.0f}", annotation_position="top",
        annotation_font=dict(color=ACCENT, size=11),
    )

    strength = "fortement" if abs(corr) > 0.5 else "modérément" if abs(corr) > 0.2 else "peu"
    fig.update_layout(
        title=dict(
            text=f"Vitesse et dribble sont {strength} liés chez les joueurs sélectionnés (r = {corr:.2f})",
            font=dict(color=TEXT_PRIMARY, size=15),
        ),
        xaxis=dict(
            title=dict(text="Vitesse (PAC, 0-100)", font=dict(color=TEXT_PRIMARY, size=14)),
            tickfont=dict(color=TEXT_PRIMARY, size=12),
            range=list(xlim), gridcolor=GRID_COLOR,
        ),
        yaxis=dict(
            title=dict(text="Dribble (DRI, 0-100)", font=dict(color=TEXT_PRIMARY, size=14)),
            tickfont=dict(color=TEXT_PRIMARY, size=12),
            range=list(ylim), gridcolor=GRID_COLOR,
        ),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        legend=dict(
            title=dict(text="Championnat", font=dict(color=TEXT_PRIMARY, size=14)),
            font=dict(color=TEXT_PRIMARY, size=12),
            orientation="v", x=1.02, y=1, xanchor="left", yanchor="top",
            bgcolor="rgba(0,0,0,0)",
            itemclick="toggle", itemdoubleclick="toggleothers",
        ),
        margin=dict(t=60, r=170, b=50, l=60),
        height=420,
    )

    why = (
        "Un nuage de points montre la relation entre deux variables quantitatives (vitesse et "
        "dribble), utile pour repérer les profils rapides et techniques. Les lignes verticales "
        "marquent les quartiles Q1 et Q3 de la vitesse, pour situer le quart le plus lent et le "
        "quart le plus rapide de la sélection. La légende est cliquable : cliquez sur un "
        "championnat pour le masquer, double-cliquez pour l'isoler."
    )
    interpretation = f"La corrélation entre vitesse et dribble est {strength} (r = {corr:.2f}) sur la sélection actuelle."
    return fig, why, interpretation
