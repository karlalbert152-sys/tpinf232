"""
Générateur de données E-commerce réalistes pour le TP INF232 EC2
Support optionnel de données personnalisées.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def generate_ecommerce_data(n_samples=5000, random_state=42):
    """Génère un dataset e-commerce réaliste avec des corrélations."""
    np.random.seed(random_state)

    categories = ["Électronique", "Mode", "Maison", "Sport", "Livres"]
    villes = ["Paris", "Lyon", "Marseille", "Bordeaux", "Lille", "Nantes", "Toulouse", "Nice"]
    canaux = ["SEO", "Instagram", "Facebook", "Google_Ads", "Email", "Direct"]
    saisons = ["Printemps", "Été", "Automne", "Hiver"]
    sexes = ["F", "M"]

    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=int(x)) for x in np.random.exponential(30, n_samples).cumsum()]
    dates = [min(d, datetime(2024, 12, 31)) for d in dates]

    categories_list = np.random.choice(categories, size=n_samples, p=[0.25, 0.30, 0.20, 0.15, 0.10])

    base_prices = {"Électronique": 450, "Mode": 65, "Maison": 120, "Sport": 85, "Livres": 18}
    prix = np.array([base_prices[c] * np.random.uniform(0.5, 2.0) for c in categories_list])

    age = np.random.normal(35, 12, n_samples).astype(int)
    age = np.clip(age, 18, 70)
    sexe = np.random.choice(sexes, size=n_samples, p=[0.52, 0.48])
    ville = np.random.choice(villes, size=n_samples)

    canal = np.random.choice(canaux, size=n_samples, p=[0.20, 0.25, 0.20, 0.20, 0.10, 0.05])
    note_produit = np.clip(np.random.normal(3.8, 1.1, n_samples), 1, 5).round(1)
    temps_sur_page = np.random.gamma(2, 40, n_samples) + 20
    temps_sur_page = temps_sur_page * (1 + 0.1 * (note_produit - 3))

    quantite = np.random.poisson(lam=1.5 + 0.3 * (note_produit - 3) + 0.01 * temps_sur_page/10)
    quantite = np.clip(quantite, 1, 10)

    saison = [saisons[(d.month % 12) // 3] for d in dates]

    saison_effect = {"Printemps": 1.0, "Été": 0.95, "Automne": 1.05, "Hiver": 1.15}
    montant_total = prix * quantite * np.array([saison_effect[s] for s in saison]) * np.random.uniform(0.9, 1.1, n_samples)

    panier_moyen = montant_total * np.random.uniform(0.85, 1.0, n_samples)

    fidelite_score = (montant_total / 100) + (temps_sur_page / 60) + np.random.normal(0, 2, n_samples)
    est_client_fidele = (fidelite_score > np.percentile(fidelite_score, 60)).astype(int)

    df = pd.DataFrame({
        "id_transaction": range(1, n_samples + 1),
        "date": dates,
        "categorie": categories_list,
        "prix_unitaire": prix.round(2),
        "quantite": quantite,
        "age_client": age,
        "sexe_client": sexe,
        "ville": ville,
        "canal_acquisition": canal,
        "note_produit": note_produit,
        "temps_sur_page_sec": temps_sur_page.round(0).astype(int),
        "saison": saison,
        "montant_total": montant_total.round(2),
        "panier_moyen": panier_moyen.round(2),
        "est_client_fidele": est_client_fidele,
    })
    return df

def get_or_generate_data(path="data/ecommerce_data.csv", n_samples=5000, custom_df=None):
    """Retourne un DataFrame. Si custom_df fourni, le retourne. Sinon charge ou génère."""
    if custom_df is not None:
        return custom_df
    path = Path(path)
    if path.exists():
        return pd.read_csv(path, parse_dates=["date"])
    df = generate_ecommerce_data(n_samples)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df
