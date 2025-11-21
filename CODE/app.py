import joblib
import os
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 

# --- 1. Configuration et Chargement des Modèles ---

# Le nom des fichiers .joblib que vous avez uploadés
MODEL_PATH = 'svm_sqli_model.joblib'
VECTORIZER_PATH = 'vectorizer.joblib'

# Variables globales pour stocker le modèle et le vectorizer chargés
loaded_vectorizer = None
loaded_model = None

# Créer l'application FastAPI
app = FastAPI(
    title="SQLI Detection API (SVM/TF-IDF)",
    description="API légère pour la classification SQL Injection utilisant SVM, remplaçant le modèle BERT trop volumineux pour le déploiement simple.",
    version="1.0"
)

# Configuration CORS (essentiel pour que l'HTML sur un navigateur puisse appeler l'API)
# '*' permet l'accès depuis n'importe quelle adresse (utile pour le développement local)
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Model pour la requête (l'entrée de l'API)
class QueryInput(BaseModel):
    """Schéma de l'entrée attendue par l'API (la requête SQL)"""
    text: str

# Fonction qui charge les modèles au DÉMARRAGE de l'API (une seule fois)
@app.on_event("startup")
def load_assets():
    """Charge le vectorizer et le modèle SVM depuis les fichiers joblib."""
    global loaded_vectorizer, loaded_model
    try:
        loaded_vectorizer = joblib.load(VECTORIZER_PATH)
        loaded_model = joblib.load(MODEL_PATH)
        print("✅ Modèle SVM et Vectorizer chargés avec succès au démarrage de l'API.")
    except FileNotFoundError:
        print(f"❌ Erreur: Fichiers de modèle manquants. Vérifiez les chemins: {MODEL_PATH} et {VECTORIZER_PATH}")
        # Si le chargement échoue, on lève une exception pour que l'API ne démarre pas sans modèle
        raise RuntimeError("Les fichiers du modèle et du vectorizer sont introuvables.")

# --- 2. Endpoint de Prédiction ---

@app.post("/predict_sqli")
def predict_sqli(query: QueryInput):
    """
    Endpoint qui reçoit une requête SQL (du front-end) et retourne la prédiction.
    """
    
    # 1. Transformation de la requête (texte -> vecteur numérique)
    # NOTE: `.transform` attend une liste
    query_vectorized = loaded_vectorizer.transform([query.text])
    
    # 2. Prédiction par le modèle SVM
    prediction = loaded_model.predict(query_vectorized) # Retourne [0] ou [1]
    
    # 3. Formatage du résultat
    is_sqli = bool(prediction[0])
    
    if is_sqli:
        result_text = "🚨 SQL INJECTION DETECTED (Label 1)"
    else:
        result_text = "✅ Normal Query (Label 0)"
    
    # Retourner la réponse au format JSON (celle que le JavaScript de index.html attend)
    return {
        "prediction": result_text,
        "is_sqli": is_sqli,
        "query": query.text
    }