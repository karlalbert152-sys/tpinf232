# TP INF232 EC2 - Analyse de Données E-commerce

**Auteur** : Étudiant 2ème Année Informatique  
**Date** : 2026  
**Secteur** : E-commerce Multi-catégories

## Description

Application complète d'analyse de données pour le secteur e-commerce, développée dans le cadre du module **INF232 EC2 (Analyse de données)**. Le projet intègre :

1. **Régression Linéaire Simple**
2. **Régression Linéaire Multiple**
3. **Réduction de Dimensionnalité (PCA)**
4. **Classification Supervisée** (Random Forest, Régression Logistique)
5. **Classification Non-Supervisée** (K-Means)

## Architecture

- `api/` : Backend **FastAPI** avec les endpoints d'analyse
- `app/` : Frontend **Streamlit** interactif
- `data/` : Dataset généré automatiquement
- `requirements.txt` : Dépendances Python

## Technologies utilisées

| Technologie | Rôle |
|-------------|------|
| FastAPI | API REST pour les modèles ML |
| Streamlit | Interface utilisateur interactive |
| Pandas | Manipulation des données |
| NumPy | Calculs numériques |
| Scikit-learn | Algorithmes de ML |
| Plotly | Visualisations interactives |

## Installation (local)

```bash
# 1. Cloner / extraire le projet
cd ecommerce_analytics

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'API FastAPI (Terminal 1)
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 5. Lancer Streamlit (Terminal 2)
cd app
streamlit run streamlit_app.py
```

## Déploiement en ligne (Streamlit Cloud - Gratuit)

La méthode la plus simple pour obtenir un lien exécutable :

1. Créer un dépôt **GitHub** public
2. Pousser les fichiers du projet
3. Se connecter à [share.streamlit.io](https://share.streamlit.io)
4. Déployer le dossier `app/streamlit_app.py`
5. Le lien généré est à envoyer au professeur

**Note** : L'application utilise directement les modules Python (pas d'appel HTTP obligatoire), ce qui permet un déploiement Streamlit Cloud très simple en un seul fichier.

## Fonctionnalités par module

### Module 1 : Régression Simple
- Choix de la variable X et Y
- Affichage du R², RMSE, coefficient
- Nuage de points réel vs prédit
- Graphique des résidus

### Module 2 : Régression Multiple
- Sélection multiple de features
- Standardisation automatique
- Tableau des coefficients
- Importance des variables

### Module 3 : PCA
- Sélection des variables à réduire
- Variance expliquée par composante
- Projection 2D interactive colorée par catégorie

### Module 4 : Classification Supervisée
- Prédiction de la fidélité client (`est_client_fidele`)
- Random Forest vs Régression Logistique
- Matrice de confusion
- Courbe de probabilités
- Rapport de classification complet

### Module 5 : Clustering (K-Means)
- Choix du nombre de clusters K
- Méthode du coude (Elbow)
- Score Silhouette
- Visualisation PCA des clusters
- Profils moyens par cluster

## Qualités de l'application

| Qualité | Implémentation |
|---------|----------------|
| **Créativité** | Secteur e-commerce original avec corrélation entre comportement client et CA |
| **Robustesse** | Gestion des erreurs, validations Pydantic, fallback local, dataset auto-généré |
| **Efficacité** | Temps d'exécution mesurés, graphiques Plotly rapides, code vectorisé NumPy |

## Captures d'écran suggérées

Pour le rendu, voici les pages à montrer :
1. Exploration des données (histogrammes)
2. Régression simple avec équation
3. PCA avec clusters colorés
4. Classification (matrice de confusion)
5. K-Means (méthode du coude)

## Contact

Lien de l'application : *(à compléter après déploiement Streamlit Cloud)*

---
*Projet réalisé dans le cadre du TP INF232 EC2.*
# tpinf232
# tpinf232
