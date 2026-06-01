import streamlit as st
import os
import fitz
from llm_processor import CVOptimizer
from document_generator import DocumentGenerator

st.set_page_config(page_title="Adapta-CV Pro", page_icon="🚀", layout="wide")

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

# Sidebar
with st.sidebar:
    st.title("🛠️ Adapta-CV Pro")
    provider = st.radio("Motor de IA:", ["groq", "deepseek"])
    api_key = st.text_input(f"API Key de {provider.capitalize()}:", value=st.secrets.get(f"{provider.upper()}_API_KEY", ""), type="password")
    template = st.selectbox("🎨 Diseño:", ["Clásico", "Moderno", "Minimalista"])
    language = st.selectbox("🌐 Idioma:", ["es", "en"])

st.title("🚀 Optimización Total: CV + Carta de Presentación")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Tu Perfil")
    uploaded_file = st.file_uploader("Sube tu CV en PDF", type="pdf")
    cv_manual = st.text_area("O pega tu texto aquí:", height=150)
    cv_text = extract_text_from_pdf(uploaded_file) if uploaded_file else cv_manual

with col2:
    st.subheader("2️⃣ La Vacante")
    job_url = st.text_input("🔗 Pega la URL del empleo (LinkedIn, etc):")
    job_manual = st.text_area("O pega la descripción manualmente:", height=150)
    
    job_text = job_manual
    if job_url and st.button("🔍 Extraer de URL"):
        with st.spinner("Leyendo vacante..."):
            optimizer = CVOptimizer(provider=provider, api_key=api_key)
            job_text = optimizer.extract_job_from_url(job_url)
            st.info(f"Contenido extraído: {job_text[:200]}...")

st.markdown("---")

if st.button("🔥 GENERAR TODO (CV + CARTA)", type="primary", use_container_width=True):
    if not api_key or not cv_text or not job_text:
        st.error("Faltan datos o API Key.")
    else:
        optimizer = CVOptimizer(provider=provider, api_key=api_key)
        with st.spinner("Optimizando CV..."):
            st.session_state.cv = optimizer.optimize_cv(cv_text, job_text, language)
        with st.spinner("Redactando Carta de Presentación..."):
            st.session_state.cl = optimizer.generate_cover_letter(cv_text, job_text, language)
        st.success("¡Listo!")

if "cv" in st.session_state:
    st.subheader("📥 Tus Documentos Listos")
    c1, c2 = st.columns(2)
    
    with c1:
        st.info("📄 CURRÍCULUM VITAE")
        st.download_button("Word", DocumentGenerator.generate_word(st.session_state.cv, template), "CV_Optimizado.docx", use_container_width=True)
        st.download_button("PDF", DocumentGenerator.generate_pdf(st.session_state.cv, template), "CV_Optimizado.pdf", use_container_width=True)
        
    with c2:
        st.info("✉️ CARTA DE PRESENTACIÓN")
        st.download_button("Word", DocumentGenerator.generate_cl_word(st.session_state.cl, st.session_state.cv.full_name, template), "Carta_Presentacion.docx", use_container_width=True)
        st.download_button("PDF", DocumentGenerator.generate_cl_pdf(st.session_state.cl, st.session_state.cv.full_name, template), "Carta_Presentacion.pdf", use_container_width=True)
    
    with st.expander("👁️ Ver Carta de Presentación"):
        st.write(st.session_state.cl)
