"""
API FastAPI - Analyse de Données E-commerce
INF232 EC2 - 2ème Année
Modules: Régression, PCA, Classification, Clustering
Version avec support de données personnalisées.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, Optional
import pandas as pd
import numpy as np
import json
import time
from pathlib import Path

# Scikit-learn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import (
    mean_squared_error, r2_score,
    accuracy_score, confusion_matrix, classification_report,
    silhouette_score
)

# Local imports
from data_generator import get_or_generate_data

# --- Variable globale pour données personnalisées ---
_custom_data = None

def set_custom_data(df: pd.DataFrame):
    global _custom_data
    _custom_data = df

def load_data():
    """Charge les données : personnalisées si définies, sinon générées."""
    return get_or_generate_data(custom_df=_custom_data)

app = FastAPI(
    title="INF232 EC2 - API Analyse E-commerce",
    description="API d'analyse de données pour le secteur e-commerce",
    version="1.0.0"
)

# CORS pour Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Modèles Pydantic (inchangés)
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    n_samples: int = Field(default=5000, ge=100, le=50000)

class RegressionSimpleRequest(BaseModel):
    target: str = "panier_moyen"
    feature: str = "temps_sur_page_sec"
    test_size: float = 0.2

class RegressionMultipleRequest(BaseModel):
    target: str = "montant_total"
    features: list[str] = ["prix_unitaire", "quantite", "age_client", "temps_sur_page_sec", "note_produit"]
    test_size: float = 0.2

class ReductionRequest(BaseModel):
    n_components: int = 2
    features: list[str] = ["prix_unitaire", "quantite", "age_client", "temps_sur_page_sec", "note_produit", "montant_total", "panier_moyen"]

class SupervisedRequest(BaseModel):
    target: str = "est_client_fidele"
    features: list[str] = ["prix_unitaire", "quantite", "age_client", "temps_sur_page_sec", "note_produit", "montant_total"]
    model_type: Literal["random_forest", "logistic_regression"] = "random_forest"
    test_size: float = 0.2

class UnsupervisedRequest(BaseModel):
    features: list[str] = ["prix_unitaire", "quantite", "age_client", "montant_total", "temps_sur_page_sec"]
    n_clusters: int = 3
    random_state: int = 42

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PERF_LOG = []

def log_perf(operation: str, duration_ms: float, details: Optional[dict] = None):
    PERF_LOG.append({
        "operation": operation,
        "duration_ms": round(duration_ms, 2),
        "timestamp": time.strftime("%H:%M:%S"),
        "details": details or {}
    })

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API INF232 EC2 - Analyse E-commerce", "status": "ok"}

@app.post("/api/v1/data/generate")
def generate_data(req: GenerateRequest):
    start = time.time()
    df = get_or_generate_data(n_samples=req.n_samples, custom_df=_custom_data)
    duration = (time.time() - start) * 1000
    log_perf("generate_data", duration, {"n_samples": req.n_samples})
    return {
        "message": f"Données générées : {len(df)} transactions",
        "shape": df.shape,
        "columns": list(df.columns),
        "preview": df.head(5).to_dict(orient="records")
    }

@app.get("/api/v1/data")
def get_data(limit: int = 100):
    df = load_data()
    return {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {k: str(v) for k, v in df.dtypes.items()},
        "data": df.head(limit).replace({np.nan: None}).to_dict(orient="records")
    }

@app.get("/api/v1/data/stats")
def get_stats():
    df = load_data()
    numeric = df.select_dtypes(include=[np.number])
    return {
        "numeric_summary": numeric.describe().round(2).to_dict(),
        "categorical_counts": {
            col: df[col].value_counts().head(10).to_dict()
            for col in df.select_dtypes(include=["object", "category"]).columns
        }
    }

# ===========================================================================
# 1. Régression Linéaire Simple
# ===========================================================================

@app.post("/api/v1/regression/simple")
def regression_simple(req: RegressionSimpleRequest):
    start = time.time()
    df = load_data()

    if req.target not in df.columns or req.feature not in df.columns:
        raise HTTPException(status_code=400, detail="Colonne cible ou feature inconnue")

    X = df[[req.feature]].values
    y = df[req.target].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=req.test_size, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    duration = (time.time() - start) * 1000
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = float(r2_score(y_test, y_pred))

    log_perf("regression_simple", duration, {"rmse": rmse, "r2": r2})

    sample_idx = np.random.choice(len(X_test), min(300, len(X_test)), replace=False)

    return {
        "model": "Régression Linéaire Simple",
        "feature": req.feature,
        "target": req.target,
        "coefficient": float(model.coef_[0]),
        "intercept": float(model.intercept_),
        "rmse": rmse,
        "r2_score": r2,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "scatter": {
            "x_real": X_test[sample_idx, 0].tolist(),
            "y_real": y_test[sample_idx].tolist(),
            "y_pred": y_pred[sample_idx].tolist()
        },
        "equation": f"{req.target} = {model.coef_[0]:.4f} * {req.feature} + {model.intercept_:.4f}",
        "execution_time_ms": round(duration, 2)
    }

# ===========================================================================
# 2. Régression Linéaire Multiple
# ===========================================================================

@app.post("/api/v1/regression/multiple")
def regression_multiple(req: RegressionMultipleRequest):
    start = time.time()
    df = load_data()

    missing = [c for c in req.features if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Features manquantes: {missing}")
    if req.target not in df.columns:
        raise HTTPException(status_code=400, detail="Target inconnu")

    X = df[req.features].values
    y = df[req.target].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=req.test_size, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_s, y_train)
    y_pred = model.predict(X_test_s)

    duration = (time.time() - start) * 1000
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = float(r2_score(y_test, y_pred))

    log_perf("regression_multiple", duration, {"rmse": rmse, "r2": r2, "features": req.features})

    importance = {f: float(abs(c)) for f, c in zip(req.features, model.coef_)}

    return {
        "model": "Régression Linéaire Multiple",
        "features": req.features,
        "target": req.target,
        "coefficients": {f: float(c) for f, c in zip(req.features, model.coef_)},
        "intercept": float(model.intercept_),
        "rmse": rmse,
        "r2_score": r2,
        "feature_importance": importance,
        "residuals": (y_test[:200] - y_pred[:200]).tolist(),
        "y_test_sample": y_test[:200].tolist(),
        "y_pred_sample": y_pred[:200].tolist(),
        "execution_time_ms": round(duration, 2)
    }

# ===========================================================================
# 3. Réduction de Dimensionnalité (PCA)
# ===========================================================================

@app.post("/api/v1/reduction/pca")
def reduction_pca(req: ReductionRequest):
    start = time.time()
    df = load_data()

    missing = [c for c in req.features if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Features manquantes: {missing}")

    X = df[req.features].values
    X = StandardScaler().fit_transform(X)

    n_comp = min(req.n_components, len(req.features))
    pca = PCA(n_components=n_comp)
    components = pca.fit_transform(X)

    duration = (time.time() - start) * 1000
    log_perf("pca", duration, {"variance_ratio": pca.explained_variance_ratio_.tolist()})

    categories = df["categorie"].tolist()

    result = {
        "method": "PCA",
        "n_components": n_comp,
        "explained_variance_ratio": [float(v) for v in pca.explained_variance_ratio_],
        "cumulative_variance": float(np.sum(pca.explained_variance_ratio_)),
        "components": components[:500].tolist(),
        "categories": categories[:500],
        "feature_names": req.features,
        "loadings": {f: pca.components_[:, i].tolist() for i, f in enumerate(req.features)},
        "execution_time_ms": round(duration, 2)
    }
    return result

# ===========================================================================
# 4. Classification Supervisée
# ===========================================================================

@app.post("/api/v1/classification/supervised")
def classification_supervised(req: SupervisedRequest):
    start = time.time()
    df = load_data()

    if req.target not in df.columns:
        raise HTTPException(status_code=400, detail="Target inconnu")

    X = df[req.features].values
    y = df[req.target].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=req.test_size, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    if req.model_type == "random_forest":
        model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    else:
        model = LogisticRegression(max_iter=1000, random_state=42)

    model.fit(X_train_s, y_train)
    y_pred = model.predict(X_test_s)

    acc = float(accuracy_score(y_test, y_pred))
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)

    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test_s)[:, 1]
    else:
        y_proba = y_pred.astype(float)

    duration = (time.time() - start) * 1000
    log_perf("classification_supervised", duration, {"accuracy": acc, "model": req.model_type})

    if hasattr(model, "feature_importances_"):
        importance = {f: float(v) for f, v in zip(req.features, model.feature_importances_)}
    else:
        importance = {f: float(v) for f, v in zip(req.features, np.abs(model.coef_[0]))}

    return {
        "model_type": req.model_type,
        "target": req.target,
        "accuracy": acc,
        "confusion_matrix": cm,
        "classification_report": report,
        "feature_importance": importance,
        "y_test": y_test.tolist(),
        "y_pred": y_pred.tolist(),
        "y_proba": y_proba.tolist(),
        "execution_time_ms": round(duration, 2)
    }

# ===========================================================================
# 5. Classification Non Supervisée (K-Means)
# ===========================================================================

@app.post("/api/v1/classification/unsupervised")
def classification_unsupervised(req: UnsupervisedRequest):
    start = time.time()
    df = load_data()

    missing = [c for c in req.features if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Features manquantes: {missing}")

    X = df[req.features].values
    X_s = StandardScaler().fit_transform(X)

    kmeans = KMeans(n_clusters=req.n_clusters, random_state=req.random_state, n_init=10)
    labels = kmeans.fit_predict(X_s)

    silhouette = float(silhouette_score(X_s, labels))

    inertias = []
    silhouettes = []
    K_range = range(2, 11)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=req.random_state, n_init=10)
        lab = km.fit_predict(X_s)
        inertias.append(float(km.inertia_))
        silhouettes.append(float(silhouette_score(X_s, lab)))

    duration = (time.time() - start) * 1000
    log_perf("kmeans", duration, {"n_clusters": req.n_clusters, "silhouette": silhouette})

    centers = kmeans.cluster_centers_.tolist()

    df["cluster"] = labels
    cluster_stats = df.groupby("cluster")[req.features].mean().round(2).to_dict(orient="index")
    cluster_sizes = df["cluster"].value_counts().to_dict()
    cluster_sizes = {int(k): int(v) for k, v in cluster_sizes.items()}

    pca_vis = PCA(n_components=2)
    X_vis = pca_vis.fit_transform(X_s)

    return {
        "method": "K-Means",
        "n_clusters": req.n_clusters,
        "silhouette_score": silhouette,
        "inertias": inertias,
        "silhouettes": silhouettes,
        "k_range": list(K_range),
        "labels": labels.tolist(),
        "centers": centers,
        "cluster_sizes": cluster_sizes,
        "cluster_stats": cluster_stats,
        "scatter_2d": X_vis[:800].tolist(),
        "execution_time_ms": round(duration, 2)
    }

# ===========================================================================
# Performances Globales
# ===========================================================================

@app.get("/api/v1/performances")
def get_performances():
    return {
        "total_operations": len(PERF_LOG),
        "operations": PERF_LOG,
        "system": "FastAPI + scikit-learn"
    }

# Lancement local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
