import streamlit as st

# Les 5 grands championnats européens, tels que nommés dans le dataset.
BIG5_LEAGUES = [
    "Premier League",
    "LALIGA EA SPORTS",
    "Bundesliga",
    "Serie A Enilive",
    "Ligue 1 McDonald's",
]


def render_filters(df):
    """Affiche les filtres dans la sidebar et renvoie (dataframe filtré, dict des filtres).
    Les valeurs par défaut reproduisent la demande du directeur sportif : un ailier rapide
    et bon dribbleur, hors des cinq grands championnats, OVR > 75."""
    st.sidebar.header("🔍 Filtres de recrutement")

    genre = st.sidebar.radio(
        "Compétition",
        ["Hommes", "Femmes"],
        help="Les notes ne sont pas comparables d'une compétition à l'autre : on ne mélange pas les deux.",
    )
    df_genre = df[df["gender"] == ("M" if genre == "Hommes" else "F")]

    leagues = st.sidebar.multiselect(
        "Championnat",
        sorted(df_genre["League"].dropna().unique()),
        help="Aucune sélection = tous les championnats",
    )
    positions = st.sidebar.multiselect(
        "Poste",
        sorted(df_genre["Position"].dropna().unique()),
        default=["LW", "RW"],
        help="LW/RW = ailier gauche/droit. Aucune sélection = tous les postes.",
    )
    ovr_min = st.sidebar.slider("Note globale (OVR) minimum", 40, 99, 75)
    pac_min = st.sidebar.slider("Vitesse (PAC) minimum", 20, 99, 70)
    dri_min = st.sidebar.slider("Dribble (DRI) minimum", 20, 99, 70)
    exclude_big5 = st.sidebar.checkbox(
        "Hors des 5 grands championnats",
        value=True,
        help="Exclut Premier League, Liga, Bundesliga, Serie A et Ligue 1 pour dénicher des profils moins exposés.",
    )

    sel = df_genre[
        (df_genre["OVR"] >= ovr_min) & (df_genre["PAC"] >= pac_min) & (df_genre["DRI"] >= dri_min)
    ]
    if leagues:
        sel = sel[sel["League"].isin(leagues)]
    if positions:
        sel = sel[sel["Position"].isin(positions)]
    if exclude_big5:
        sel = sel[~sel["League"].isin(BIG5_LEAGUES)]

    filters = {
        "genre": genre,
        "leagues": leagues,
        "positions": positions,
        "ovr_min": ovr_min,
        "pac_min": pac_min,
        "dri_min": dri_min,
        "exclude_big5": exclude_big5,
    }
    return sel, filters
