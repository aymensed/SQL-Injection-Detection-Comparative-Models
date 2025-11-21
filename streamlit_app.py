import streamlit as st
import joblib
import os
# from pydantic import BaseModel # Inutile si l'API n'est plus appelée

# --- 0. Configuration et Chargement des Modèles (Mise en cache) ---

# NOTE: Si vous avez mis ces fichiers dans un dossier 'code/', changez les chemins ici:
# MODEL_PATH = 'CODE/svm_sqli_model.joblib'
# VECTORIZER_PATH = 'CODE/vectorizer.joblib'
MODEL_PATH = 'CODE/svm_sqli_model.joblib'
VECTORIZER_PATH = 'CODE/vectorizer.joblib'

# st.cache_resource garantit que les modèles ne sont chargés qu'UNE SEULE FOIS.
@st.cache_resource
def load_models():
    """
    Charge le modèle SVM et le vectorizer TF-IDF.
    Toutes les commandes d'affichage Streamlit doivent être évitées ici.
    """
    try:
        # Vérifiez que les fichiers existent avant d'essayer de les charger
        if not os.path.exists(VECTORIZER_PATH) or not os.path.exists(MODEL_PATH):
             raise FileNotFoundError
             
        loaded_vectorizer = joblib.load(VECTORIZER_PATH)
        loaded_model = joblib.load(MODEL_PATH)
        
        return loaded_vectorizer, loaded_model
    except FileNotFoundError:
        st.error(f"❌ Erreur FATALE: Fichiers de modèle manquants. Assurez-vous que '{MODEL_PATH}' et '{VECTORIZER_PATH}' sont présents.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des modèles: {e}")
        st.stop()


# --- Appel de la fonction de chargement (Correction de l'erreur précédente) ---
try:
    loaded_vectorizer, loaded_model = load_models()
    st.toast("✅ Modèles SVM et Vectorizer chargés avec succès.", icon="💾") 
except Exception:
    st.stop() 


# --- 1. Fonction de Prédiction ---

def predict_sqli(query_text: str):
    """Effectue la prédiction avec le modèle chargé (Logique de app.py)."""
    # 1. Transformation de la requête
    query_vectorized = loaded_vectorizer.transform([query_text])
    
    # 2. Prédiction
    prediction = loaded_model.predict(query_vectorized)
    is_sqli = bool(prediction[0])

    if is_sqli:
        result_text = "🚨 SQL INJECTION DETECTED (Label 1)"
        result_icon = "🚨"
    else:
        result_text = "✅ No SQL Injection Detected (Label 0)"
        result_icon = "✅"

    return is_sqli, result_text, result_icon

# --- Fonction de Callback pour les exemples ---

def update_query_input(text):
    """Met à jour st.session_state.query_input."""
    st.session_state.query_input = text


# --- 2. Interface Streamlit (Recréation de index.html) ---

st.set_page_config(
    page_title="SQL Injection Detector (SVM/TF-IDF)",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Style Customisé (pour imiter le look de l'HTML)
st.markdown("""
<style>
/* Masquer le header et le footer par défaut de Streamlit */
.stApp > header { visibility: hidden; height: 0; } 
.stApp > footer { visibility: hidden; } 
/* Style pour la boîte d'accuracy (metric-display) */
.metric-box {
    background-color: #e2f0e6;
    border: 2px solid #28a745;
    padding: 15px 20px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.metric-value {
    font-size: 2.5em;
    color: #28a745;
    font-weight: bold;
    display: block;
    letter-spacing: 1px;
}
/* Style du bouton d'analyse pour une meilleure visibilité */
button[kind="primary"] {
    background-color: #007bff;
    border-color: #007bff;
}
button[kind="primary"]:hover {
    background-color: #0056b3;
    border-color: #0056b3;
}
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown("<h1 style='text-align: center;'>SQL Injection Detection with ML Models 🛡️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-top: -10px;'>Real-time analysis powered by <b>SVM model</b> with <b>TF-IDF features</b></p>", unsafe_allow_html=True)

# Lien GitHub (positionné en haut à droite)
st.markdown("""
<div style='text-align: right; margin-top: -30px; margin-bottom: 20px;'>
    <a href="https://github.com/aymensed/SQL-Injection-Detection-Comparative-Models" target="_blank" style='color: #007bff; text-decoration: none; display: inline-flex; align-items: center; gap: 5px; font-weight: bold;'>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg> Voir le projet sur GitHub
    </a>
</div>
""", unsafe_allow_html=True)

# Boîte d'Accuracy (metric-display)
st.markdown("""
<div class="metric-box">
    <div style='font-size: 1.1em; color: #343a40; margin-bottom: 5px;'>SVM Model Performance on Unseen Data</div>
    <div class="metric-value">ACCURACY: 98.56%</div>
    <p style='margin: 5px 0 0 0; font-size: 0.9em;'>(Modèle actuellement intégré)</p>
</div>
""", unsafe_allow_html=True)

# --- 1. Enter Query to Test (Interactive Card) ---
st.header("1. Enter Query to Test")

st.markdown("""
Entrez la requête utilisateur ci-dessous pour déterminer si elle est une tentative **Normal (✅)** ou **SQL Injection (SQLi) (🚨)**.
""")

# Initialisation de la session state pour l'entrée
if 'query_input' not in st.session_state:
    st.session_state.query_input = ""

# Colonnes pour l'entrée et le bouton
col_text, col_button = st.columns([4, 1])

with col_text:
    # Le st.text_area est lié à la clé "query_input"
    user_input = st.text_area(
        "Requête SQL à analyser :",
        height=150,
        placeholder="Exemples: ' OR 1=1 -- or SELECT name, email FROM users;",
        key="query_input",
        label_visibility="collapsed"
    )

with col_button:
    # Alignement vertical du bouton
    st.markdown("<div style='height: 110px;'></div>", unsafe_allow_html=True) 
    analyze_button = st.button("Analyze Query with SVM", type="primary", use_container_width=True)

# Exemples cliquables
with st.expander("Cliquez ici pour essayer des exemples (Copie dans la zone de texte)"):
    examples = [
        ("SELECT name, email FROM users", "Normal", "#c3e6cb"),
        (" ' OR 1=1 -- ", "SQLi", "#f5c6cb"),
        ("UPDATE products SET price=10 WHERE id=5", "Normal", "#c3e6cb"),
        ("'; DROP TABLE users-- ", "SQLi", "#f5c6cb")
    ]
    
    example_cols = st.columns(len(examples))
    for i, (text, label, color) in enumerate(examples):
        # Utilisation du paramètre on_click pour appeler la fonction de callback
        example_cols[i].button(
            f"[{label}] {text}", 
            key=f"example_{i}", 
            use_container_width=True,
            on_click=update_query_input,
            args=(text,) # Argument pour la fonction update_query_input
        )


# Logique de Prédiction et Affichage du Résultat
if analyze_button and user_input.strip():
    with st.spinner("⚙️ Analyzing query with SVM model..."):
        is_sqli, result_text, result_icon = predict_sqli(user_input)

    st.markdown("---")
    st.subheader("Résultat de l'Analyse")

    if is_sqli:
        st.error(f"**{result_icon} {result_text}**", icon="🚨")
    else:
        st.success(f"**{result_icon} {result_text}**", icon="✅")
        
    st.markdown(f"**Requête Analysée :**")
    st.code(user_input, language="sql")
elif analyze_button and not user_input.strip():
    st.warning("Veuillez entrer une requête SQL pour l'analyse.", icon="⚠️")

st.markdown("---")

# --- 2. Implemented Models Overview (Modèles/Statistiques) ---
st.header("2. Implemented Models Overview")

# Données de la table de comparaison de performance
performance_data = [
    ["SVM (Current)", "98.56%", "99.86%", "96.25%", "99.02%"],
    ["LR", "98.12%", "99.72%", "95.25%", "97.44%"],
    ["MLP", "99.44%", "99.51%", "98.98%", "99.25%"],
    ["RNN", "99.06%", "100%", "97.51%", "98.74%"],
    ["LSTM", "99.62%", "99.73%", "99.25%", "99.49%"],
    ["BERT", "99.92%", "100%", "99.78%", "99.89%"]
]

# Affichage des statistiques dans un tableau Streamlit (dataframe)
st.subheader("Performance Metrics Comparison (Test Data)")
st.dataframe(
    data=performance_data,
    column_config={
        0: st.column_config.TextColumn("Model"), 
        1: st.column_config.TextColumn("Accuracy"), 
        2: st.column_config.TextColumn("Precision"), 
        3: st.column_config.TextColumn("Recall"), 
        4: st.column_config.TextColumn("F1 Score")
    },
    hide_index=True,
    height=240
)

# Descriptions complètes pour les expanders
model_details = {
    "SVM (Current)": {
        "desc": "Nous avons utilisé un **Support Vector Machine** avec un noyau linéaire (`kernel='linear'`) et C=0.1. Les requêtes ont été transformées par TF-IDF avec 3000 caractéristiques max. (Modèle actuellement intégré)",
        "metrics": dict(zip(performance_data[0][1:], ["Accuracy", "Precision", "Recall", "F1 Score"]))
    },
    "LR": {
        "desc": "Classifieur **Logistic Regression** entraîné pour détecter les charges utiles SQL injection à l'aide de fonctionnalités TF-IDF (3000 caractéristiques max.).",
        "metrics": dict(zip(performance_data[1][1:], ["Accuracy", "Precision", "Recall", "F1 Score"]))
    },
    "MLP": {
        "desc": "Réseau de neurones **Multi-Layer Perceptron (MLP)** utilisant des fonctions d'activation ReLU avec trois couches cachées (512, 256, 128 unités). Vectorisation par TF-IDF.",
        "metrics": dict(zip(performance_data[2][1:], ["Accuracy", "Precision", "Recall", "F1 Score"]))
    },
    "RNN": {
        "desc": "Réseau de neurones récurrent (**RNN**) formé pour détecter les modèles séquentiels dans les tentatives d'injection SQL en préservant la sensibilité à la casse et la syntaxe SQL.",
        "metrics": dict(zip(performance_data[3][1:], ["Accuracy", "Precision", "Recall", "F1 Score"]))
    },
    "LSTM": {
        "desc": "Réseau **LSTM** (Long Short-Term Memory) pour reconnaître les modèles séquentiels, en préservant l'intégrité de la syntaxe SQL (sans filtres de caractères ni mise en minuscule).",
        "metrics": dict(zip(performance_data[4][1:], ["Accuracy", "Precision", "Recall", "F1 Score"]))
    },
    "BERT": {
        "desc": "Modèle **BERT** (Bidirectional Encoder Representations from Transformers) sélectionné pour sa haute capacité à comprendre le sens et le contexte des requêtes SQL de manière bidirectionnelle.",
        "metrics": dict(zip(performance_data[5][1:], ["Accuracy", "Precision", "Recall", "F1 Score"]))
    }
}

st.subheader("Détails des Modèles")
for model_name, data in model_details.items():
    with st.expander(f"### {model_name}"):
        st.markdown(data["desc"])
        
        # Afficher les métriques sous forme de colonnes pour les stats individuelles
        cols_metrics = st.columns(4)
        for i, (label, value) in enumerate(data["metrics"].items()):
            cols_metrics[i].metric(label, value)

st.markdown("---")

# --- 3. Informative Section (TF-IDF/SVM & Dataset) ---
st.header("3. Project Methodology & Dataset")

info_cols = st.columns(2)

# Carte Info 1 : TF-IDF & SVM
with info_cols[0]:
    with st.container(border=True):
        st.subheader("What is TF-IDF & SVM? 🤖")
        st.markdown("""
        La **Support Vector Machine (SVM)** est un algorithme qui trouve l'hyperplan optimal maximisant la marge entre les classes.
        
        

        Le **TF-IDF (Term Frequency-Inverse Document Frequency)** est la technique utilisée pour transformer les requêtes textuelles en vecteurs numériques exploitables par le modèle SVM.

        **Implémentation Actuelle :** Notre modèle SVM utilise un **noyau linéaire** avec **C=0.1** et un **TfidfVectorizer** avec 3000 caractéristiques.
        """)
        


# Carte Info 2 : Dataset
with info_cols[1]:
    with st.container(border=True):
        st.subheader("Dataset Used 📊")
        st.markdown("""
        Le modèle a été entraîné sur un ensemble de données de **30,614 requêtes étiquetées** pour la détection SQLi :

        * **Label 0 (Normal)** : Requêtes SQL standard et entrées utilisateur bénignes.
        * **Label 1 (SQLi)** : Divers types d'attaques par injection SQL.

        **Prétraitement :** Les chaînes de caractères ont été tokenisées, mises en minuscules, et vectorisées par l'objet **TfidfVectorizer** sauvegardé (le fichier `vectorizer.joblib`).
        """)

st.markdown("---")

# --- 4. Performance Visualizations (Graphs Section) ---
st.header("4. Performance Visualizations")


col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.subheader("Training Loss Curve (BERT Example)")
    st.image(
        "loss.png",
        caption="Figure 4.4 Courbe de performance (Loss) pour le modèle BERT.",
        use_column_width=True
    )

with col_graph2:
    st.subheader("Accuracy Curve (BERT Example)")
    st.image(
        "accuracy.png",
        caption="Figure 4.5 Courbe d'Accuracy sur l'ensemble de Validation (BERT).",
        use_column_width=True
    )

st.markdown("---")

# --- Footer ---
st.markdown("""
<div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin-top: 40px;'>
    <p style='margin: 0;'>Explorez le projet complet, le code source et la documentation détaillée :</p>
    <a href="https://github.com/aymensed/SQL-Injection-Detection-Comparative-Models" target="_blank" style='color: #007bff; text-decoration: none; font-weight: bold; font-size: 1.1em;'>
        🔗 GitHub Repository: SQL-Injection-Detection-Comparative-Models
    </a>
</div>
""", unsafe_allow_html=True)



