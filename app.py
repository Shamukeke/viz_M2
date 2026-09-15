import streamlit as st
import pandas as pd

from filters import render_filters
from charts import POSITION_LABELS
from charts.distribution import plot_distribution
from charts.comparaison import plot_comparaison, plot_radar, plot_position_distribution
from charts.relation import plot_relation
from charts.age import plot_age_curve
from charts.budget import plot_budget_top5
from valuation import add_estimated_value, estimate_value, format_value

st.set_page_config(page_title="Cellule de recrutement", layout="wide", page_icon="🧭")


@st.cache_data
def load_data():
    return pd.read_csv("data/all_players_clean.csv")


df = load_data()

st.title("🧭 Cellule de recrutement")
st.caption(
    "Brief du directeur sportif : trouver un ailier rapide et bon dribbleur, hors des cinq "
    "grands championnats, avec une note globale supérieure à 75. Les filtres ci-contre sont "
    "réglés sur ce brief par défaut — élargissez-les pour explorer d'autres profils."
)
with st.expander("🔤 Lexique des sigles (OVR, PAC...)"):
    lex1, lex2 = st.columns(2)
    lex1.markdown(
        "**Notes globales (0 à 99)**\n"
        "- **OVR** — Note globale (Overall)\n"
        "- **PAC** — Vitesse (Pace)\n"
        "- **SHO** — Tir (Shooting)\n"
        "- **PAS** — Passe (Passing)\n"
        "- **DRI** — Dribble (Dribbling)\n"
        "- **DEF** — Défense (Defending)\n"
        "- **PHY** — Physique (Physicality)"
    )
    lex2.markdown(
        "**Postes**\n" + "\n".join(f"- **{code}** — {label}" for code, label in POSITION_LABELS.items())
    )

st.subheader("🔎 Rechercher un joueur")
st.caption(
    "Recherche libre parmi les 17 700+ joueurs du dataset, indépendamment des filtres "
    "ci-contre — pour vérifier le profil et la valeur estimée d'un joueur précis."
)
recherche = st.selectbox(
    "Nom du joueur",
    options=[""] + sorted(df["Name"].dropna().unique()),
    index=0,
    help="Tapez quelques lettres pour filtrer la liste.",
)
if recherche:
    player = df[df["Name"] == recherche].iloc[0]
    valeur = estimate_value(player["OVR"], player["Age"], player["Position"])
    with st.container(border=True):
        pc1, pc2 = st.columns([2, 3])
        poste_label = POSITION_LABELS.get(player["Position"], player["Position"])
        pc1.markdown(
            f"**{player['Name']}** — {player['Age']} ans\n\n"
            f"{poste_label} ({player['Position']}) · {player['Team']}\n\n"
            f"Championnat : {player['League']} · Nation : {player['Nation']}"
        )
        pm1, pm2, pm3, pm4 = pc2.columns(4)
        pm1.metric("OVR", int(player["OVR"]))
        pm2.metric("PAC", int(player["PAC"]))
        pm3.metric("DRI", int(player["DRI"]))
        pm4.metric("Valeur estimée", format_value(valeur))
        st.caption(
            "**Valeur estimée, pas une vraie valeur de marché** : le dataset ne contient "
            "aucune donnée de transfert. Elle est calculée à partir de l'OVR, l'âge et le "
            "poste (courbe exponentielle par OVR + primes jeunesse/poste offensif), pour "
            "donner un ordre de grandeur indicatif, pas une évaluation fiable."
        )

st.divider()

sel, active_filters = render_filters(df)
baseline = df[df["gender"] == ("M" if active_filters["genre"] == "Hommes" else "F")]

if sel.empty:
    st.warning("Aucun joueur ne correspond à ces critères. Élargissez un ou plusieurs filtres.")
    st.stop()

# --- Chiffres clés (comparés à la moyenne de la compétition choisie) -------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Joueurs sélectionnés", len(sel), help=f"Sur {len(baseline)} joueurs dans cette compétition")
c2.metric("OVR moyen", round(sel["OVR"].mean(), 1), delta=round(sel["OVR"].mean() - baseline["OVR"].mean(), 1))
c3.metric("PAC moyen", round(sel["PAC"].mean(), 1), delta=round(sel["PAC"].mean() - baseline["PAC"].mean(), 1))
c4.metric("DRI moyen", round(sel["DRI"].mean(), 1), delta=round(sel["DRI"].mean() - baseline["DRI"].mean(), 1))
st.caption("Écarts (▲/▼) par rapport à la moyenne de tous les joueurs de la même compétition.")

# --- Meilleur profil correspondant au brief --------------------------------
top = sel.sort_values("OVR", ascending=False).iloc[0]
with st.container(border=True):
    st.markdown("##### 🏆 Meilleur profil pour ce brief")
    tc1, tc2 = st.columns([2, 3])
    poste_label = POSITION_LABELS.get(top["Position"], top["Position"])
    tc1.markdown(
        f"**{top['Name']}** — {top['Age']} ans\n\n"
        f"{poste_label} ({top['Position']}) · {top['Team']}\n\n"
        f"Championnat : {top['League']} · Nation : {top['Nation']}"
    )
    tm1, tm2, tm3 = tc2.columns(3)
    tm1.metric("OVR", int(top["OVR"]))
    tm2.metric("PAC", int(top["PAC"]))
    tm3.metric("DRI", int(top["DRI"]))

st.divider()

# --- Trois graphiques --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribution")
    fig, why, interpretation = plot_distribution(sel)
    st.pyplot(fig)
    st.caption(f"**Pourquoi ce graphique ?** {why}")
    st.caption(f"**Lecture :** {interpretation}")

with col2:
    st.subheader("Comparaison par poste")
    fig, why, interpretation = plot_comparaison(sel)
    st.pyplot(fig)
    st.caption(f"**Pourquoi ce graphique ?** {why}")
    st.caption(f"**Lecture :** {interpretation}")

st.subheader("Relation vitesse / dribble")
fig, why, interpretation = plot_relation(sel)
st.plotly_chart(fig, width="stretch")
st.caption(f"**Pourquoi ce graphique ?** {why}")
st.caption(f"**Lecture :** {interpretation}")

st.subheader("Courbe de forme par âge")
fig, why, interpretation = plot_age_curve(sel)
st.pyplot(fig, width="stretch")
st.caption(f"**Pourquoi ce graphique ?** {why}")
st.caption(f"**Lecture :** {interpretation}")

st.divider()

# --- Bonus : radar de comparaison ------------------------------------------
with st.expander("🎯 Pour aller plus loin : comparer deux profils (radar)"):
    st.caption(
        "Le radar n'est lisible qu'à 2-3 joueurs et l'ordre des axes change la forme perçue : "
        "à utiliser pour un face-à-face ciblé, pas pour explorer toute la sélection."
    )
    noms = sel.sort_values("OVR", ascending=False)["Name"].tolist()
    if len(noms) >= 2:
        col_a, col_b = st.columns(2)
        joueur_a = col_a.selectbox("Joueur A", noms, index=0)
        joueur_b = col_b.selectbox("Joueur B", noms, index=1)
        if joueur_a != joueur_b:
            col_radar, col_pie = st.columns(2)
            with col_radar:
                st.pyplot(plot_radar(sel, joueur_a, joueur_b), width="stretch")
            with col_pie:
                fig_pie, why_pie, interpretation_pie = plot_position_distribution(sel)
                st.pyplot(fig_pie, width="stretch")
                st.caption(f"**Lecture :** {interpretation_pie}")
        else:
            st.info("Choisissez deux joueurs différents.")
    else:
        st.info("Il faut au moins deux joueurs dans la sélection pour comparer.")

st.divider()

# --- Tableau des meilleurs profils ------------------------------------------
st.subheader("Meilleurs profils")
colonnes = ["Name", "Age", "Position", "Team", "League", "OVR", "PAC", "SHO", "PAS", "DRI", "PHY"]
st.dataframe(
    sel.sort_values("OVR", ascending=False)[colonnes].reset_index(drop=True),
    width="stretch",
)

st.divider()

# --- Budget de recrutement ---------------------------------------------------
st.subheader("💰 Recrutable avec ce budget")
st.caption(
    "Parmi les joueurs correspondant aux filtres ci-contre, lesquels entrent dans un budget "
    "donné ? Basé sur la valeur estimée (voir zone de recherche ci-dessus)."
)
budget = st.number_input(
    "Budget disponible (M€)", min_value=0.0, value=20.0, step=1.0, format="%.1f",
)
sel_valorisee = add_estimated_value(sel)
abordables = sel_valorisee[sel_valorisee["ValeurEstimee"] <= budget].sort_values(
    "OVR", ascending=False
)
st.caption(
    f"{len(abordables)} joueur(s) recrutables avec {format_value(budget)}, "
    f"sur {len(sel)} dans la sélection actuelle."
)
if abordables.empty:
    st.info("Aucun joueur de la sélection actuelle n'entre dans ce budget. Augmentez le budget ou élargissez les filtres.")
else:
    st.dataframe(
        abordables[["Name", "Age", "Position", "Team", "League", "OVR", "PAC", "DRI", "ValeurEstimee"]]
        .rename(columns={"ValeurEstimee": "Valeur estimée (M€)"})
        .reset_index(drop=True),
        width="stretch",
    )

    st.markdown("###### Top 5 des recrues les plus chères encore accessibles")
    fig, why, interpretation = plot_budget_top5(abordables, budget)
    st.pyplot(fig)
    st.caption(f"**Pourquoi ce graphique ?** {why}")
    st.caption(f"**Lecture :** {interpretation}")
