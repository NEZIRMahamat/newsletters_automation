# ui/app_streamlit.py

import requests
import pandas as pd
import streamlit as st

API_URL = "http://127.0.0.1:8000/rss-enriched-test"


@st.cache_data(ttl=300)
def fetch_articles():
    """Récupère les articles enrichis depuis l'API FastAPI."""
    resp = requests.get(API_URL)
    resp.raise_for_status()
    return resp.json()


def main():
    st.set_page_config(
        page_title="Newsletter IA – Multi-agents",
        layout="wide",
    )

    st.title("📰 Newsletter IA – Multi-agents")

    # Chargement des données
    with st.spinner("Récupération des articles…"):
        articles = fetch_articles()

    if not articles:
        st.warning("Aucun article trouvé pour le moment.")
        return

    df = pd.DataFrame(articles)

    # Barre latérale : filtres
    st.sidebar.header("🧮 Filtres")

    # Filtres possibles en fonction des champs de ArticleEnrichi
    types_dispo = sorted(df["type_contenu"].dropna().unique())
    audiences_dispo = sorted(df["audience"].dropna().unique())

    type_filtre = st.sidebar.multiselect(
        "Type de contenu",
        options=types_dispo,
        default=types_dispo,
    )

    audience_filtre = st.sidebar.multiselect(
        "Niveau d'audience",
        options=audiences_dispo,
        default=audiences_dispo,
    )

    score_min = st.sidebar.slider(
        "Score minimal",
        min_value=int(df.get("score_global", 0).min() if "score_global" in df else 0),
        max_value=int(df.get("score_global", 100).max() if "score_global" in df else 100),
        value=60,
        step=1,
    ) if "score_global" in df else 0

    # Application des filtres
    df_filtered = df.copy()

    if type_filtre:
        df_filtered = df_filtered[df_filtered["type_contenu"].isin(type_filtre)]

    if audience_filtre:
        df_filtered = df_filtered[df_filtered["audience"].isin(audience_filtre)]

    if "score_global" in df_filtered.columns:
        df_filtered = df_filtered[df_filtered["score_global"] >= score_min]

    # Tri par score si dispo
    if "score_global" in df_filtered.columns:
        df_filtered = df_filtered.sort_values("score_global", ascending=False)

    st.subheader(f"📚 Articles ({len(df_filtered)})")

    # Affichage carte par carte
    for _, row in df_filtered.iterrows():
        with st.container(border=True):
            header = f"**{row['title']}**"
            if "score_global" in row and not pd.isna(row["score_global"]):
                header += f"  — ⭐ {int(row['score_global'])}/100"

            st.markdown(header)

            meta = f"_Source : {row['source']}_"
            if row.get("published_at"):
                meta += f" • _Publié le : {row['published_at']}_"
            st.markdown(meta)

            st.write(row.get("short_summary", ""))
            with st.expander("Voir le résumé détaillé"):
                st.write(row.get("detailed_summary", ""))

            if isinstance(row.get("tags"), list) and row["tags"]:
                tags_str = " ".join([f"`{t}`" for t in row["tags"]])
                st.markdown(f"**Tags :** {tags_str}")

            if row.get("link"):
                st.markdown(f"[🔗 Lire l'article complet]({row['link']})")

            if row.get("score_details"):
                with st.expander("Détails du score"):
                    st.write(row["score_details"])

            st.markdown("---")


if __name__ == "__main__":
    main()
