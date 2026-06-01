import streamlit as st
import os
import pypdf
from datetime import datetime
from llm_processor import CVOptimizer
from document_generator import DocumentGenerator

st.set_page_config(page_title="Adapta-CV ATS", page_icon="📄", layout="wide")

# Estilos
st.markdown("""
<style>
    .main-header { text-align: center; color: #1f77b4; margin-bottom: 20px; }
    .stTextArea textarea { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/942/942748.png", width=100)
    st.markdown("### 🛠️ Configuración")
    
    provider = st.radio("Motor de IA:", ["groq", "deepseek"])
    
    # Secrets o Input
    default_key = st.secrets.get(f"{provider.upper()}_API_KEY", "")
    api_key = st.text_input(f"API Key de {provider.capitalize()}:", value=default_key, type="password")
    
    st.markdown("---")
    template = st.selectbox("🎨 Plantilla de Diseño:", ["Clásico", "Moderno", "Minimalista"])
    language = st.selectbox("🌐 Idioma Destino:", ["es", "en"], format_func=lambda x: "Español" if x=="es" else "English")

st.markdown("<h1 class='main-header'>📄 Adapta-CV: Optimización ATS Genuina</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 1️⃣ Tu Perfil Actual")
    upload_method = st.tabs(["📤 Subir PDF", "📝 Pegar Texto"])
    
    cv_text = ""
    with upload_method[0]:
        uploaded_file = st.file_uploader("Sube tu CV actual en PDF", type="pdf")
        if uploaded_file:
            cv_text = extract_text_from_pdf(uploaded_file)
            st.success("✅ PDF leído correctamente")
            with st.expander("Ver texto extraído"):
                st.write(cv_text[:500] + "...")
                
    with upload_method[1]:
        cv_text_manual = st.text_area("Pega aquí tu CV o LinkedIn:", height=200)
        if cv_text_manual:
            cv_text = cv_text_manual

with col2:
    st.markdown("### 2️⃣ Vacante de Empleo")
    job_desc = st.text_area("Pega la descripción del empleo (Job Description):", height=265, placeholder="Requisitos, responsabilidades...")

st.markdown("---")

if st.button("🚀 Generar CV Optimizado", type="primary", use_container_width=True):
    if not api_key:
        st.error(f"Por favor configura la API Key de {provider} en la barra lateral.")
    elif not cv_text or not job_desc:
        st.error("Falta tu CV o la descripción del empleo.")
    else:
        with st.spinner("Analizando y adaptando tu perfil..."):
            try:
                optimizer = CVOptimizer(provider=provider, api_key=api_key)
                optimized_cv = optimizer.optimize_cv(cv_text, job_desc, language)
                st.session_state.optimized_cv = optimized_cv
                st.success("¡Optimización completada!")
            except Exception as e:
                st.error(f"Error: {e}")

if "optimized_cv" in st.session_state:
    cv = st.session_state.optimized_cv
    st.markdown("### 📥 Descarga tu CV Optimizado")
    
    c1, c2 = st.columns(2)
    with c1:
        word_data = DocumentGenerator.generate_word(cv, template)
        st.download_button("📄 Descargar Word (.docx)", word_data, f"CV_Optimizado_{template}.docx", use_container_width=True)
    with c2:
        pdf_data = DocumentGenerator.generate_pdf(cv, template)
        st.download_button("📕 Descargar PDF", pdf_data, f"CV_Optimizado_{template}.pdf", use_container_width=True)
    
    with st.expander("🔍 Revisar contenido adaptado"):
        st.json(cv.dict())
