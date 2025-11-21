import joblib
import os

MODEL_PATH = 'svm_sqli_model.joblib'
VECTORIZER_PATH = 'vectorizer.joblib'

print("--- Lancement du Test d'Intégrité ---")

try:
    # 1. Tentative de chargement
    vectorizer = joblib.load(VECTORIZER_PATH)
    model = joblib.load(MODEL_PATH)
    print("✅ Chargement des fichiers réussi.")
    
    # 2. Tentative d'utilisation (le point de rupture dans l'API)
    test_query = "SELECT name FROM users WHERE id = 1;"
    query_vectorized = vectorizer.transform([test_query])
    prediction = model.predict(query_vectorized)
    
    print(f"✅ Utilisation du modèle réussie. Résultat de prédiction: {prediction[0]}")
    print("\nLe problème n'est pas le modèle, mais l'environnement.")

except Exception as e:
    print("\n❌ Échec du test d'utilisation.")
    print(f"Erreur DÉTAILLÉE : {e}")
    print("\nLe problème est très probablement une corruption dans le fichier joblib lui-même.")

print("--- Fin du Test ---")