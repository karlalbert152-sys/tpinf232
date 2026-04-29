"""
NEO ANALYTICS · E-commerce Intelligence
INF232 EC2 - Version Ultra Premium - Noir Absolu / Cyberpunk
Design: Fond noir profond, néons cyan/violet, glassmorphism extrême
Fonctionnalités: Données générées + Upload CSV/Excel + Saisie manuelle + Modèles ML
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys, io, time
from pathlib import Path

# --- Configuration des chemins ---
CURRENT_DIR = Path(__file__).parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# --- Import des modules métier ---
from data_generator import get_or_generate_data, generate_ecommerce_data
try:
    from main import (
        regression_simple, regression_multiple,
        reduction_pca, classification_supervised,
        classification_unsupervised, load_data, PERF_LOG
    )
    # Tentative d'import de set_custom_data (peut ne pas exister)
    try:
        from main import set_custom_data
    except ImportError:
        # Définition locale si absente
        def set_custom_data(df):
            if 'custom_dataset' not in st.session_state:
                st.session_state.custom_dataset = None
            st.session_state.custom_dataset = df
            # Tentative de modifier la variable globale de main
            try:
                import main
                main._custom_data = df
            except:
                pass
except ImportError as e:
    st.error(f"Erreur d'import : veuillez placer ce fichier dans le même dossier que main.py et data_generator.py\nDétail: {e}")
    st.stop()

# --- Configuration page (doit être la première commande streamlit) ---
st.set_page_config(
    page_title="DEMANOU-FOUDJI-KARL-ALBERT-KUETE-24F2995",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Initialisation session ---
if 'custom_dataset' not in st.session_state:
    st.session_state.custom_dataset = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = "generated"
if 'manual_records' not in st.session_state:
    st.session_state.manual_records = []

def update_main_custom_data(df):
    """Met à jour les données personnalisées dans session + main.py"""
    st.session_state.custom_dataset = df
    set_custom_data(df)

def get_active_df():
    """Retourne le DataFrame actif (personnalisé ou généré)"""
    if st.session_state.custom_dataset is not None and st.session_state.data_source != "generated":
        return st.session_state.custom_dataset
    return get_or_generate_data()

def make_req(**kwargs):
    class R: pass
    r = R()
    for k, v in kwargs.items(): setattr(r, k, v)
    return r

# ============================================================
#  CSS : NOIR ABSOLU + CYBERPUNK FUTURISTE
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&family=Share+Tech+Mono&display=swap');

* {
    font-family: 'Rajdhani', sans-serif;
}

/* ------- ARRIÈRE-PLAN NOIR PROFOND ------- */
.stApp {
    background: #000000 !important;
    background-image: radial-gradient(circle at 20% 30%, rgba(0, 20, 40, 0.4) 0%, #000000 90%),
                      repeating-linear-gradient(0deg, rgba(0, 255, 255, 0.02) 0px, rgba(0, 255, 255, 0.02) 1px, transparent 1px, transparent 5px);
    background-blend-mode: overlay;
    color: #e0e0ff;
}

/* ------- SIDEBAR NOIRE AVEC VERRE ------- */
section[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0.9) !important;
    backdrop-filter: blur(16px);
    border-right: 2px solid rgba(0, 245, 255, 0.4) !important;
    box-shadow: 8px 0 30px rgba(0, 245, 255, 0.1);
}

/* ------- CARTES MÉTRIQUES (GLASS NOIR) ------- */
.neo-card, .metric-card, [data-testid="stMetric"] {
    background: rgba(0, 0, 0, 0.75) !important;
    backdrop-filter: blur(12px);
    border: 1px solid #00f5ff;
    border-radius: 16px;
    padding: 1rem 1.2rem;
    transition: all 0.25s ease;
    box-shadow: 0 0 15px rgba(0, 245, 255, 0.2);
}
.neo-card:hover, .metric-card:hover {
    transform: translateY(-4px);
    border-color: #39ff14;
    box-shadow: 0 0 30px rgba(57, 255, 20, 0.3);
}
.neo-card-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    color: #7a85b8;
}
.neo-card-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #00f5ff;
    text-shadow: 0 0 15px #00f5ff;
    margin: 0.2rem 0;
}
.neo-card-delta {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.8rem;
    color: #39ff14;
}

/* ------- BOUTONS NÉONS ------- */
.stButton > button {
    background: linear-gradient(95deg, #001a2a, #000000) !important;
    border: 1px solid #00f5ff !important;
    border-radius: 30px !important;
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    color: #00f5ff !important;
    box-shadow: 0 0 12px rgba(0, 245, 255, 0.6);
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(95deg, #003a5a, #001a2a) !important;
    border-color: #39ff14 !important;
    box-shadow: 0 0 25px rgba(57, 255, 20, 0.8);
    transform: translateY(-2px);
}
.stFormSubmitButton > button {
    background: linear-gradient(95deg, #00f5ff, #b347ff) !important;
    color: #000000 !important;
    font-weight: 900 !important;
    border: none !important;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.8);
}
.stFormSubmitButton > button:hover {
    box-shadow: 0 0 35px rgba(179, 71, 255, 0.9);
}

/* ------- TITRES ------- */
.hero-title {
    font-family: 'Orbitron', monospace;
    font-size: 2.5rem;
    font-weight: 900;
    background: linear-gradient(135deg, #00f5ff, #b347ff);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow: 0 0 20px rgba(0,245,255,0.5);
}
.hero-sub {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    letter-spacing: 0.1em;
    color: #b347ff;
}
.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: #00f5ff;
    border-left: 4px solid #b347ff;
    padding-left: 1rem;
    margin: 1rem 0;
    text-shadow: 0 0 12px #00f5ff;
}

/* ------- INPUTS / SELECTEURS NOIRS ------- */
div[data-baseweb="select"] > div, .stMultiSelect [data-baseweb="select"] > div,
.stNumberInput > div > div > input, .stTextInput > div > div > input {
    background: #000000cc !important;
    border: 1px solid #00f5ff88 !important;
    border-radius: 8px !important;
    color: #e0e0ff !important;
}

.stSlider > div > div {
    background-color: #00f5ff !important;
}
.stSlider > div > div > div {
    background-color: #b347ff !important;
}

/* ------- DATA FRAME ------- */
.stDataFrame {
    background: #000000aa !important;
    border: 1px solid #00f5ff33 !important;
    border-radius: 12px;
}

/* ------- TABS ------- */
.stTabs [data-baseweb="tab-list"] {
    background: #000000aa !important;
    border-radius: 30px;
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    color: #7a85b8;
}
.stTabs [aria-selected="true"] {
    background: #00f5ff22 !important;
    color: #00f5ff !important;
    border-bottom: 2px solid #00f5ff;
}

/* ------- UPLOAD ------- */
[data-testid="stFileUploader"] {
    background: #000000cc !important;
    border: 2px dashed #00f5ff !important;
    border-radius: 16px;
}
[data-testid="stFileUploader"]:hover {
    border-color: #b347ff !important;
}

/* ------- BADGES SOURCE ------- */
.data-badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    padding: 4px 12px;
    border-radius: 40px;
    display: inline-block;
}
.badge-generated { background: #00f5ff11; border: 1px solid #00f5ff; color: #00f5ff; }
.badge-uploaded  { background: #b347ff11; border: 1px solid #b347ff; color: #b347ff; }
.badge-manual    { background: #39ff1411; border: 1px solid #39ff14; color: #39ff14; }

/* ------- FOOTER ------- */
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
#  HELPERS GRAPHIQUES (NÉON)
# ============================================================
def neo_metric(label, value, delta=None, color="#00f5ff"):
    delta_html = f'<div class="neo-card-delta">↗ {delta}</div>' if delta else ""
    return f"""
    <div class="neo-card" style="text-align:center;">
        <div class="neo-card-label">{label}</div>
        <div class="neo-card-value" style="color:{color};">{value}</div>
        {delta_html}
    </div>
    """

def neo_scatter(x, y_real, y_pred, title, xlabel, ylabel):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y_real, mode='markers', name='Réel',
        marker=dict(color='#00f5ff', opacity=0.55, size=6,
                    line=dict(color='rgba(0,245,255,0.3)', width=0.5))))
    fig.add_trace(go.Scatter(x=x, y=y_pred, mode='markers', name='Prédit',
        marker=dict(color='#ff2d95', opacity=0.55, size=6, symbol='x')))
    mn, mx = float(min(min(x), min(y_real))), float(max(max(x), max(y_real)))
    fig.add_trace(go.Scatter(x=[mn,mx], y=[mn,mx], mode='lines', name='Idéal',
        line=dict(color='#39ff14', dash='dash', width=1.5)))
    fig.update_layout(title=title, xaxis_title=xlabel, yaxis_title=ylabel,
                      height=400, paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0.4)',
                      font=dict(color='#e0e0ff'))
    return fig

def neo_residuals(y_test, y_pred):
    residuals = np.array(y_test) - np.array(y_pred)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y_pred, y=residuals, mode='markers',
        marker=dict(color='#b347ff', opacity=0.6, size=5),
        name='Résidus'))
    fig.add_hline(y=0, line_dash="dash", line_color="#ff2d95", line_width=1.5)
    fig.update_layout(title="Analyse des Résidus", xaxis_title="Prédictions",
                      yaxis_title="Résidus", height=400,
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0.4)')
    return fig

# ============================================================
#  SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div style="font-family:Orbitron;font-size:1.2rem;font-weight:900;color:#00f5ff;text-align:center;">DEMANOU-FOUDJI-KARL-ALBERT-KUETE-24F2995</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Share Tech Mono;font-size:0.6rem;color:#b347ff;text-align:center;margin-bottom:1rem;">E-COMMERCE · CYBER INTEL</div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("", [
        "🌐 Tableau de Bord",
        "📂 Source des Données",
        "📊 Exploration",
        "〔1〕 Régression Simple",
        "〔2〕 Régression Multiple",
        "〔3〕 PCA · Réduction",
        "〔4〕 Classification",
        "〔5〕 Clustering",
        "⚡ Performances",
    ], label_visibility="collapsed")
    st.markdown("---")
    src = st.session_state.data_source
    badge_class = "badge-generated" if src == "generated" else ("badge-uploaded" if src == "uploaded" else "badge-manual")
    badge_txt = "DONNÉES GÉNÉRÉES" if src == "generated" else ("FICHIER CHARGÉ" if src == "uploaded" else "SAISIE MANUELLE")
    st.markdown(f'<div style="text-align:center;"><span class="data-badge {badge_class}">● {badge_txt}</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("INF232 EC2 · Université d'Été")

# ============================================================
#  TABLEAU DE BORD
# ============================================================
if menu == "🌐 Tableau de Bord":
    st.markdown('<div class="hero-title" style="text-align:center;">NEO ANALYTICS · E-commerce Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub" style="text-align:center;">Analyse prédictive · Régression · PCA · Classification · Clustering</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    df = get_active_df()
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(neo_metric("TRANSACTIONS", f"{len(df):,}", "actif"), unsafe_allow_html=True)
    with col2:
        ca = df["montant_total"].sum()/1000 if "montant_total" in df.columns else 0
        st.markdown(neo_metric("CA TOTAL (k€)", f"{ca:,.1f}", "dataset", "#b347ff"), unsafe_allow_html=True)
    with col3:
        pm = df["panier_moyen"].mean() if "panier_moyen" in df.columns else 0
        st.markdown(neo_metric("PANIER MOYEN (€)", f"{pm:.2f}", "moyenne", "#ff2d95"), unsafe_allow_html=True)
    with col4:
        fid = df["est_client_fidele"].sum() if "est_client_fidele" in df.columns else 0
        st.markdown(neo_metric("CLIENTS FIDÈLES", f"{fid:,}", "certifiés", "#39ff14"), unsafe_allow_html=True)
    with col5:
        num_cols = len(df.select_dtypes(include=[np.number]).columns)
        st.markdown(neo_metric("FEATURES NUM.", f"{num_cols}", f"{len(df.columns)} total", "#ff9100"), unsafe_allow_html=True)

    st.markdown("---")
    col_left, col_right = st.columns(2)
    with col_left:
        if "montant_total" in df.columns and "date" in df.columns:
            try:
                df2 = df.copy()
                df2["date"] = pd.to_datetime(df2["date"])
                ts = df2.groupby(df2["date"].dt.to_period("M"))["montant_total"].sum().reset_index()
                ts["date"] = ts["date"].astype(str)
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=ts["date"], y=ts["montant_total"], mode='lines', fill='tozeroy',
                                         line=dict(color='#00f5ff', width=2), fillcolor='rgba(0,245,255,0.05)'))
                fig.update_layout(title="Évolution du CA Mensuel", height=300,
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.3)')
                st.plotly_chart(fig, use_container_width=True)
            except: pass
    with col_right:
        if "categorie" in df.columns:
            counts = df["categorie"].value_counts()
            fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.5,
                                   marker=dict(colors=["#00f5ff","#b347ff","#ff2d95","#39ff14","#ff9100"])))
            fig.update_layout(title="Répartition par Catégorie", height=300,
                              paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">MODULES DISPONIBLES</div>', unsafe_allow_html=True)
    m1, m2, m3, m4, m5 = st.columns(5)
    for col, (icon, title, desc, color) in zip([m1,m2,m3,m4,m5],
        [("〔1〕","Régression Simple","Prédiction univariée","#00f5ff"),
         ("〔2〕","Régression Multiple","Modélisation multivariée","#b347ff"),
         ("〔3〕","PCA","Réduction dimensionnelle","#ff2d95"),
         ("〔4〕","Classification","Random Forest / LogReg","#39ff14"),
         ("〔5〕","Clustering","K-Means segmentation","#ff9100")]):
        with col:
            st.markdown(f"""
            <div class="neo-card" style="text-align:center;">
                <div style="font-family:Orbitron;font-size:1.2rem;color:{color};">{icon}</div>
                <div style="font-family:Orbitron;font-size:0.65rem;color:{color};">{title}</div>
                <div style="font-size:0.7rem;color:#aaa;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
#  SOURCE DES DONNÉES (Import / Saisie)
# ============================================================
elif menu == "📂 Source des Données":
    st.markdown('<div class="section-header">📂 SOURCE DES DONNÉES</div>', unsafe_allow_html=True)
    tab_gen, tab_upload, tab_form = st.tabs(["⚙️ GÉNÉRÉES", "📤 UPLOAD FICHIER", "✏️ SAISIE MANUELLE"])

    with tab_gen:
        st.markdown("### Données synthétiques e-commerce")
        with st.form("gen_form"):
            col1, col2 = st.columns(2)
            with col1: n_samples = st.number_input("Nombre de transactions", 500, 50000, 5000, 500)
            with col2: random_seed = st.number_input("Seed", 0, 9999, 42)
            submitted = st.form_submit_button("⚙️ GÉNÉRER")
        if submitted:
            with st.spinner("Génération..."):
                df = generate_ecommerce_data(int(n_samples), int(random_seed))
                update_main_custom_data(df)
                st.session_state.data_source = "generated"
            st.success(f"✅ {len(df):,} transactions générées !")
            st.dataframe(df.head(8), use_container_width=True)
        if st.button("🔄 Charger depuis cache (fichier existant)"):
            df = get_or_generate_data()
            update_main_custom_data(df)
            st.session_state.data_source = "generated"
            st.rerun()

    with tab_upload:
        st.markdown("### Charger un fichier CSV / Excel")
        uploaded = st.file_uploader("Glissez votre fichier", type=["csv","xlsx","xls"])
        if uploaded:
            col1, col2, col3 = st.columns(3)
            with col1: sep = st.selectbox("Séparateur", [",",";","\\t","|"], index=0)
            with col2: enc = st.selectbox("Encodage", ["utf-8","latin-1","cp1252"])
            with col3: header = st.checkbox("En-tête", True)
            if st.button("📤 CHARGER"):
                try:
                    if uploaded.name.endswith(".csv"):
                        s = "\t" if sep=="\\t" else sep
                        df_up = pd.read_csv(uploaded, sep=s, encoding=enc, header=0 if header else None)
                    else:
                        df_up = pd.read_excel(uploaded, header=0 if header else None)
                    df_up.columns = [c.strip().lower().replace(" ", "_") for c in df_up.columns]
                    update_main_custom_data(df_up)
                    st.session_state.data_source = "uploaded"
                    st.success(f"✅ {len(df_up):,} lignes chargées")
                    st.dataframe(df_up.head(10), use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur : {e}")
        st.markdown("---")
        st.markdown("**Modèle CSV téléchargeable :**")
        template = pd.DataFrame({
            "id_transaction":[1,2,3],"date":["2024-01-15","2024-01-16","2024-01-17"],
            "categorie":["Électronique","Mode","Maison"],"prix_unitaire":[299.99,59.90,149.00],
            "quantite":[1,2,1],"age_client":[32,25,45],"sexe_client":["M","F","F"],
            "ville":["Paris","Lyon","Marseille"],"canal_acquisition":["Google_Ads","Instagram","SEO"],
            "note_produit":[4.5,3.8,4.2],"temps_sur_page_sec":[180,95,210],
            "saison":["Hiver","Hiver","Hiver"],"montant_total":[299.99,119.80,149.00],
            "panier_moyen":[254.99,101.83,126.65],"est_client_fidele":[1,0,1]
        })
        csv_data = template.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ TÉLÉCHARGER MODÈLE", csv_data, "neo_template.csv", "text/csv")

    with tab_form:
        st.markdown("### Saisie manuelle de transactions")
        col_f, col_p = st.columns([3,2])
        with col_f:
            with st.form("manual_form", clear_on_submit=True):
                st.markdown("**Nouvelle transaction**")
                c1, c2 = st.columns(2)
                with c1:
                    cat = st.selectbox("Catégorie", ["Électronique","Mode","Maison","Sport","Livres"])
                    prix = st.number_input("Prix unitaire (€)", 0.01, 10000.0, 99.99, 0.01)
                    qty = st.number_input("Quantité", 1, 100, 1)
                    age = st.number_input("Âge client", 18, 90, 30)
                with c2:
                    sex = st.selectbox("Sexe", ["F","M"])
                    note = st.slider("Note produit", 1.0, 5.0, 4.0, 0.1)
                    ville = st.selectbox("Ville", ["Paris","Lyon","Marseille","Bordeaux","Lille","Nantes","Toulouse","Nice"])
                    canal = st.selectbox("Canal", ["SEO","Instagram","Facebook","Google_Ads","Email","Direct"])
                tps = st.number_input("Temps sur page (sec)", 5, 3600, 120)
                saison = st.selectbox("Saison", ["Printemps","Été","Automne","Hiver"])
                fidele = st.checkbox("Client fidèle")
                submitted = st.form_submit_button("➕ AJOUTER")
            if submitted:
                effect = {"Printemps":1.0,"Été":0.95,"Automne":1.05,"Hiver":1.15}
                montant = prix * qty * effect.get(saison,1.0)
                panier = montant * 0.92
                rec = {
                    "id_transaction": len(st.session_state.manual_records)+1,
                    "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                    "categorie": cat, "prix_unitaire": round(prix,2), "quantite": qty,
                    "age_client": age, "sexe_client": sex, "ville": ville,
                    "canal_acquisition": canal, "note_produit": float(note),
                    "temps_sur_page_sec": tps, "saison": saison,
                    "montant_total": round(montant,2), "panier_moyen": round(panier,2),
                    "est_client_fidele": 1 if fidele else 0
                }
                st.session_state.manual_records.append(rec)
                st.success(f"Transaction #{rec['id_transaction']} ajoutée")
        with col_p:
            n_rec = len(st.session_state.manual_records)
            st.markdown(f"""
            <div class="neo-card" style="text-align:center;">
                <div class="neo-card-label">SAISIES</div>
                <div class="neo-card-value">{n_rec}</div>
            </div>
            """, unsafe_allow_html=True)
            if n_rec > 0:
                df_man = pd.DataFrame(st.session_state.manual_records)
                st.dataframe(df_man[["categorie","prix_unitaire","quantite","montant_total"]].tail(5), use_container_width=True)
                if st.button("🚀 UTILISER CES DONNÉES"):
                    if n_rec >= 5:
                        update_main_custom_data(df_man)
                        st.session_state.data_source = "manual"
                        st.success("Données manuelles activées !")
                    else:
                        st.warning("Au moins 5 transactions requises")
                if st.button("🗑️ EFFACER TOUT"):
                    st.session_state.manual_records = []
                    st.rerun()
                st.download_button("⬇️ EXPORTER CSV", df_man.to_csv(index=False).encode("utf-8"), "saisie_manuelle.csv", "text/csv")

# ============================================================
#  EXPLORATION (simplifié mais complet)
# ============================================================
elif menu == "📊 Exploration":
    st.markdown('<div class="section-header">📊 EXPLORATION DES DONNÉES</div>', unsafe_allow_html=True)
    df = get_active_df()
    st.markdown(f'<span class="data-badge {"badge-generated" if st.session_state.data_source=="generated" else "badge-uploaded" if st.session_state.data_source=="uploaded" else "badge-manual"}">● {len(df):,} lignes · {len(df.columns)} colonnes</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 APERÇU", "📈 STATISTIQUES", "🎨 VISUALISATIONS"])
    with tab1:
        st.dataframe(df.head(20), use_container_width=True)
    with tab2:
        num_df = df.select_dtypes(include=[np.number])
        st.dataframe(num_df.describe().round(3), use_container_width=True)
        if len(num_df.columns) > 1:
            corr = num_df.corr().round(2)
            fig = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns,
                                       colorscale=[[0,"#000000"],[0.5,"#b347ff"],[1,"#00f5ff"]],
                                       text=corr.values, texttemplate="%{text}"))
            fig.update_layout(title="Matrice de Corrélation", height=500,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0.3)')
            st.plotly_chart(fig, use_container_width=True)
    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            if "categorie" in df.columns:
                fig = px.histogram(df, x="categorie", color="categorie", title="Catégories", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            if "montant_total" in df.columns and "categorie" in df.columns:
                fig = px.box(df, x="categorie", y="montant_total", color="categorie", title="Montant par catégorie")
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            if "canal_acquisition" in df.columns:
                counts = df["canal_acquisition"].value_counts()
                fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.5))
                fig.update_layout(title="Canaux d'acquisition")
                st.plotly_chart(fig, use_container_width=True)
            if "temps_sur_page_sec" in df.columns and "panier_moyen" in df.columns:
                fig = px.scatter(df.sample(min(500,len(df))), x="temps_sur_page_sec", y="panier_moyen",
                                 color="categorie" if "categorie" in df.columns else None, opacity=0.6,
                                 title="Temps vs Panier")
                st.plotly_chart(fig, use_container_width=True)

# ============================================================
#  RÉGRESSION SIMPLE
# ============================================================
elif menu == "〔1〕 Régression Simple":
    st.markdown('<div class="section-header">〔1〕 RÉGRESSION LINÉAIRE SIMPLE</div>', unsafe_allow_html=True)
    df = get_active_df()
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != "id_transaction"]
    with st.form("reg_simple"):
        c1, c2, c3 = st.columns(3)
        with c1: feat = st.selectbox("VARIABLE X", num_cols)
        with c2: target = st.selectbox("VARIABLE Y", [c for c in num_cols if c != feat])
        with c3: test = st.slider("Test %", 10, 40, 20)
        sub = st.form_submit_button("🚀 LANCER")
    if sub:
        with st.spinner("Calcul..."):
            update_main_custom_data(df)
            req = make_req(feature=feat, target=target, test_size=test/100)
            try:
                res = regression_simple(req)
            except Exception as e:
                st.error(f"Erreur : {e}")
                st.stop()
        st.success("Terminé !")
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("R²", f"{res['r2_score']:.4f}")
        m2.metric("RMSE", f"{res['rmse']:.3f}")
        m3.metric("Coefficient", f"{res['coefficient']:.4f}")
        m4.metric("Temps", f"{res['execution_time_ms']:.1f} ms")
        st.markdown(f"**Équation :** `{res['equation']}`")
        col_l, col_r = st.columns(2)
        with col_l:
            st.plotly_chart(neo_scatter(res["scatter"]["x_real"], res["scatter"]["y_real"],
                                        res["scatter"]["y_pred"], "Prédictions vs Réel", feat, target),
                            use_container_width=True)
        with col_r:
            st.plotly_chart(neo_residuals(res["scatter"]["y_real"], res["scatter"]["y_pred"]),
                            use_container_width=True)

# ============================================================
#  RÉGRESSION MULTIPLE
# ============================================================
elif menu == "〔2〕 Régression Multiple":
    st.markdown('<div class="section-header">〔2〕 RÉGRESSION MULTIPLE</div>', unsafe_allow_html=True)
    df = get_active_df()
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != "id_transaction"]
    with st.form("reg_multi"):
        c1, c2 = st.columns(2)
        with c1: target = st.selectbox("CIBLE", num_cols)
        with c2: test = st.slider("Test %", 10,40,20, key="ts_multi")
        feats = st.multiselect("FEATURES", [c for c in num_cols if c != target], default=[c for c in num_cols if c != target][:4])
        sub = st.form_submit_button("📐 LANCER")
    if sub and len(feats)>=2:
        with st.spinner("Calcul..."):
            update_main_custom_data(df)
            req = make_req(target=target, features=feats, test_size=test/100)
            try:
                res = regression_multiple(req)
            except Exception as e:
                st.error(f"Erreur : {e}")
                st.stop()
        st.success("Terminé !")
        m1,m2,m3 = st.columns(3)
        m1.metric("R²", f"{res['r2_score']:.4f}")
        m2.metric("RMSE", f"{res['rmse']:.3f}")
        m3.metric("Temps", f"{res['execution_time_ms']:.1f} ms")
        imp = pd.DataFrame({"Feature":list(res["feature_importance"].keys()),
                            "Importance":list(res["feature_importance"].values())}).sort_values("Importance", ascending=True)
        fig = px.bar(imp, x="Importance", y="Feature", orientation='h', title="Importance des variables")
        st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(neo_residuals(res["y_test_sample"], res["y_pred_sample"]), use_container_width=True)
        with st.expander("Coefficients"):
            coef = pd.DataFrame({"Variable":res["features"], "Coefficient":list(res["coefficients"].values())})
            st.dataframe(coef, use_container_width=True)

# ============================================================
#  PCA
# ============================================================
elif menu == "〔3〕 PCA · Réduction":
    st.markdown('<div class="section-header">〔3〕 ANALYSE EN COMPOSANTES PRINCIPALES</div>', unsafe_allow_html=True)
    df = get_active_df()
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ["id_transaction","est_client_fidele"]]
    with st.form("pca_form"):
        feats = st.multiselect("VARIABLES", num_cols, default=num_cols[:6] if len(num_cols)>=6 else num_cols)
        n_comp = st.radio("COMPOSANTES", [2,3], index=0, horizontal=True)
        sub = st.form_submit_button("⟳ APPLIQUER PCA")
    if sub and len(feats)>=2:
        with st.spinner("Calcul PCA..."):
            update_main_custom_data(df)
            req = make_req(features=feats, n_components=int(n_comp))
            try:
                res = reduction_pca(req)
            except Exception as e:
                st.error(f"Erreur : {e}")
                st.stop()
        m1,m2,m3 = st.columns(3)
        m1.metric("Composantes", res["n_components"])
        m2.metric("Variance cumulée", f"{res['cumulative_variance']:.1%}")
        m3.metric("Temps", f"{res['execution_time_ms']:.1f} ms")
        var_df = pd.DataFrame({"Composante":[f"PC{i+1}" for i in range(len(res["explained_variance_ratio"]))],
                               "Variance":res["explained_variance_ratio"]})
        fig = px.bar(var_df, x="Composante", y="Variance", title="Variance expliquée")
        st.plotly_chart(fig, use_container_width=True)
        comps = np.array(res["components"])
        cats = res["categories"]
        vis = pd.DataFrame({"PC1":comps[:,0], "PC2":comps[:,1] if comps.shape[1]>1 else 0, "Catégorie":cats})
        fig = px.scatter(vis, x="PC1", y="PC2", color="Catégorie", title="Projection PCA", opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
#  CLASSIFICATION
# ============================================================
elif menu == "〔4〕 Classification":
    st.markdown('<div class="section-header">〔4〕 CLASSIFICATION SUPERVISÉE</div>', unsafe_allow_html=True)
    df = get_active_df()
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != "id_transaction"]
    target_options = [c for c in ["est_client_fidele"] if c in df.columns] + num_cols[:1]
    with st.form("class_form"):
        c1, c2 = st.columns(2)
        with c1: model = st.selectbox("MODÈLE", ["random_forest","logistic_regression"])
        with c2: target = st.selectbox("TARGET", target_options)
        feats = st.multiselect("FEATURES", [c for c in num_cols if c != target], default=[c for c in num_cols if c != target][:5])
        test = st.slider("Test %", 10,40,20, key="ts_class")
        sub = st.form_submit_button("🧠 ENTRAÎNER")
    if sub and len(feats)>=2:
        with st.spinner("Entraînement..."):
            update_main_custom_data(df)
            req = make_req(target=target, features=feats, model_type=model, test_size=test/100)
            try:
                res = classification_supervised(req)
            except Exception as e:
                st.error(f"Erreur : {e}")
                st.stop()
        st.success("Modèle entraîné !")
        m1,m2,m3 = st.columns(3)
        m1.metric("Accuracy", f"{res['accuracy']:.2%}")
        m2.metric("Modèle", model.replace("_"," ").title())
        m3.metric("Temps", f"{res['execution_time_ms']:.1f} ms")
        col_cm, col_imp = st.columns(2)
        with col_cm:
            cm = np.array(res["confusion_matrix"])
            fig = go.Figure(go.Heatmap(z=cm, text=cm, texttemplate="%{text}", colorscale=[[0,"#000"],[1,"#00f5ff"]]))
            fig.update_layout(title="Matrice de confusion")
            st.plotly_chart(fig, use_container_width=True)
        with col_imp:
            imp = pd.DataFrame({"Feature":list(res["feature_importance"].keys()),
                                "Importance":list(res["feature_importance"].values())}).sort_values("Importance", ascending=True)
            fig = px.bar(imp, x="Importance", y="Feature", orientation='h', title="Importance")
            st.plotly_chart(fig, use_container_width=True)
        y_proba = np.array(res["y_proba"])
        y_test = np.array(res["y_test"])
        sorted_idx = np.argsort(y_proba)
        roc_df = pd.DataFrame({"Index":range(len(y_proba)), "Probabilité":y_proba[sorted_idx], "Classe":y_test[sorted_idx]})
        fig = px.scatter(roc_df, x="Index", y="Probabilité", color="Classe", title="Distribution des probabilités")
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Rapport détaillé"):
            report = pd.DataFrame(res["classification_report"]).transpose().round(3)
            st.dataframe(report, use_container_width=True)

# ============================================================
#  CLUSTERING
# ============================================================
elif menu == "〔5〕 Clustering":
    st.markdown('<div class="section-header">〔5〕 CLUSTERING K‑MEANS</div>', unsafe_allow_html=True)
    df = get_active_df()
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ["id_transaction","est_client_fidele"]]
    with st.form("cluster_form"):
        feats = st.multiselect("VARIABLES POUR CLUSTERING", num_cols, default=num_cols[:5] if len(num_cols)>=5 else num_cols)
        k = st.slider("NOMBRE DE CLUSTERS (K)", 2, 8, 3)
        sub = st.form_submit_button("🌀 LANCER K‑MEANS")
    if sub and len(feats)>=2:
        with st.spinner("Clustering..."):
            update_main_custom_data(df)
            req = make_req(features=feats, n_clusters=k)
            try:
                res = classification_unsupervised(req)
            except Exception as e:
                st.error(f"Erreur : {e}")
                st.stop()
        st.success("Clustering terminé !")
        m1,m2,m3 = st.columns(3)
        m1.metric("Silhouette", f"{res['silhouette_score']:.3f}")
        m2.metric("Clusters", res["n_clusters"])
        m3.metric("Temps", f"{res['execution_time_ms']:.1f} ms")
        elbow = pd.DataFrame({"K":res["k_range"], "Inertie":res["inertias"], "Silhouette":res["silhouettes"]})
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(elbow, x="K", y="Inertie", markers=True, title="Méthode du coude")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.line(elbow, x="K", y="Silhouette", markers=True, title="Silhouette par K")
            st.plotly_chart(fig, use_container_width=True)
        scatter = np.array(res["scatter_2d"])
        labels = res["labels"]
        vis = pd.DataFrame({"Dim1":scatter[:,0], "Dim2":scatter[:,1], "Cluster":[f"C{l}" for l in labels[:len(scatter)]]})
        fig = px.scatter(vis, x="Dim1", y="Dim2", color="Cluster", title="Projection des clusters", opacity=0.8)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("Statistiques par cluster"):
            stats = pd.DataFrame(res["cluster_stats"]).transpose().round(2)
            st.dataframe(stats, use_container_width=True)

# ============================================================
#  PERFORMANCES
# ============================================================
elif menu == "⚡ Performances":
    st.markdown('<div class="section-header">⚡ PERFORMANCES</div>', unsafe_allow_html=True)
    if len(PERF_LOG)==0:
        st.info("Aucune opération enregistrée. Lancez des analyses.")
    else:
        perf = pd.DataFrame(PERF_LOG)
        st.dataframe(perf, use_container_width=True)
        fig = px.bar(perf, x="operation", y="duration_ms", color="duration_ms", title="Temps d'exécution (ms)")
        st.plotly_chart(fig, use_container_width=True)
        total = perf["duration_ms"].sum()
        st.metric("Temps total", f"{total:.1f} ms")
        if st.button("🗑️ RÉINITIALISER"):
            PERF_LOG.clear()
            st.rerun()

# --- Footer ---
st.markdown("---")
st.markdown('<div style="text-align:center;font-family:Share Tech Mono;font-size:0.6rem;color:#3a4070;">NEO ANALYTICS · INF232 EC2 · v2.0 · Cyber Edition</div>', unsafe_allow_html=True)
