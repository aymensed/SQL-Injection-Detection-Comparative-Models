import streamlit as st
import requests
import json
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="SQL Injection Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background-color: #007bff;
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #e2f0e6;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #28a745;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-normal {
        background-color: #d4edda;
        color: #28a745;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin-top: 1rem;
    }
    .result-sqli {
        background-color: #f8d7da;
        color: #dc3545;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin-top: 1rem;
    }
    .example-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .model-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #007bff;
    }
    .current-model {
        border-left: 4px solid #28a745;
        background-color: #f0f8ff;
    }
</style>
""", unsafe_allow_html=True)

def predict_query(query_text, api_url):
    """Fonction pour appeler l'API FastAPI"""
    try:
        response = requests.post(
            api_url,
            json={"text": query_text},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return None, f"Connection Error: {str(e)}"

# En-tête principal
st.markdown("""
<div class="main-header">
    <h1>SQL Injection Detection with ML Models 🛡️</h1>
    <p>Real-time analysis powered by SVM model with TF-IDF features</p>
</div>
""", unsafe_allow_html=True)

# Métrique principale
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="metric-card">
        <h2>SVM Model Performance</h2>
        <h1 style="color: #28a745; font-size: 3em; margin: 0;">98.56%</h1>
        <p>Accuracy on Unseen Data</p>
    </div>
    """, unsafe_allow_html=True)

# Configuration de l'API
st.sidebar.header("🔧 Configuration")
api_url = st.sidebar.text_input(
    "API URL", 
    value="http://localhost:8000/predict_sqli",
    help="URL de votre API FastAPI"
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Instructions:**
1. Démarrez votre API FastAPI
2. Laissez l'URL par défaut ou modifiez-la
3. Testez vos requêtes SQL
""")

# Section interactive
st.header("🔍 1. Test Your SQL Query")
st.markdown("Enter the user query below to determine if it is a **Normal** or **SQL Injection (SQLi)** attempt.")

# Zone de texte pour la requête
query = st.text_area(
    "SQL Query Input",
    height=150,
    placeholder="Examples: ' OR 1=1 -- or SELECT name, email FROM users;",
    key="query_input",
    label_visibility="collapsed"
)

# Exemples cliquables
st.markdown("#### 💡 Try these examples:")
examples_col1, examples_col2 = st.columns(2)

with examples_col1:
    if st.button("**Normal**: SELECT users", use_container_width=True):
        st.session_state.query_input = "SELECT name, email FROM users"
    if st.button("**Normal**: UPDATE products", use_container_width=True):
        st.session_state.query_input = "UPDATE products SET price=10 WHERE id=5"

with examples_col2:
    if st.button("**SQLi**: OR 1=1", use_container_width=True):
        st.session_state.query_input = "' OR 1=1 --"
    if st.button("**SQLi**: DROP TABLE", use_container_width=True):
        st.session_state.query_input = "'; DROP TABLE users--"

# Bouton d'analyse
if st.button("🚀 Analyze Query with SVM", type="primary", use_container_width=True):
    if query.strip():
        with st.spinner("⚙️ Analyzing query with SVM model..."):
            result, error = predict_query(query, api_url)
            
            if error:
                st.error(error)
                if "Connection" in error:
                    st.info("💡 Make sure your FastAPI server is running:\n\n```bash\nuvicorn app:app --reload\n```")
            else:
                if result["is_sqli"]:
                    st.markdown(f"""
                    <div class="result-sqli">
                        <h3>🚨 SQL Injection Detected!</h3>
                        <p><strong>Prediction:</strong> {result['prediction']}</p>
                        <p><strong>Query analyzed:</strong> {result['query'][:100]}{'...' if len(result['query']) > 100 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-normal">
                        <h3>✅ Normal Query</h3>
                        <p><strong>Prediction:</strong> {result['prediction']}</p>
                        <p><strong>Query analyzed:</strong> {result['query'][:100]}{'...' if len(result['query']) > 100 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("🛑 Please enter a query to analyze.")

# Section modèles
st.header("📊 2. Models Performance")

# Tableau de performance
performance_data = {
    "Model": ["SVM (Current)", "Logistic Regression", "MLP", "RNN", "LSTM", "BERT"],
    "Accuracy": ["98.56%", "98.12%", "99.44%", "99.06%", "99.62%", "99.92%"],
    "Precision": ["99.86%", "99.72%", "99.51%", "100%", "99.73%", "100%"],
    "Recall": ["96.25%", "95.25%", "98.98%", "97.51%", "99.25%", "99.78%"],
    "F1 Score": ["99.02%", "97.44%", "99.25%", "98.74%", "99.49%", "99.89%"]
}

df = pd.DataFrame(performance_data)
styled_df = df.style.apply(
    lambda x: ['background-color: #f0f8ff' if x['Model'] == 'SVM (Current)' else '' for _ in x], 
    axis=1
)

st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Section informations modèles
st.header("🤖 3. Models Overview")

models_col1, models_col2 = st.columns(2)

with models_col1:
    st.markdown("""
    <div class="model-card current-model">
        <h4>✅ Support Vector Machine (SVM) - Currently Integrated</h4>
        <p><strong>Architecture:</strong> Linear kernel with C=0.1</p>
        <p><strong>Features:</strong> TF-IDF (3000 max features)</p>
        <p><strong>Preprocessing:</strong> Tokenization, lowercasing, deduplication</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="model-card">
        <h4>Logistic Regression</h4>
        <p><strong>Architecture:</strong> L1 penalty with liblinear solver</p>
        <p><strong>Features:</strong> TF-IDF vectorization</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="model-card">
        <h4>Multilayer Perceptron (MLP)</h4>
        <p><strong>Architecture:</strong> 512-256-128 hidden layers</p>
        <p><strong>Activation:</strong> ReLU/Sigmoid</p>
    </div>
    """, unsafe_allow_html=True)

with models_col2:
    st.markdown("""
    <div class="model-card">
        <h4>Recurrent Neural Network (RNN)</h4>
        <p><strong>Architecture:</strong> SimpleRNN with 128 units</p>
        <p><strong>Embedding:</strong> 128 dimensions</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="model-card">
        <h4>Long Short-Term Memory (LSTM)</h4>
        <p><strong>Architecture:</strong> Stacked LSTM (256→128)</p>
        <p><strong>Embedding:</strong> 256 dimensions</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="model-card">
        <h4>BERT (Bidirectional Encoder)</h4>
        <p><strong>Architecture:</strong> BERTBASE (12 layers)</p>
        <p><strong>Training:</strong> Fine-tuned with OneCycleLR</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center;">
    <p><strong>🔗 GitHub Repository:</strong> 
    <a href="https://github.com/aymensed/SQL-Injection-Detection-Comparative-Models" target="_blank">
        SQL-Injection-Detection-Comparative-Models
    </a></p>
    <p style="color: #666; font-size: 0.9em;">Real-time SQL Injection Detection using Machine Learning and Deep Learning Models</p>
</div>
""", unsafe_allow_html=True)