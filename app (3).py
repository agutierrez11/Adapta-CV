import streamlit as st
import os
import fitz
from llm_processor import CVOptimizer
from document_generator import DocumentGenerator

st.set_page_config(page_title="Adapta-CV Pro", page_icon="🚀", layout="wide")

# Estilos Pro
st.markdown("""
<style>
    .main-header { text-align: center; color: #1f77b4; margin-bottom: 20px; }
    .match-box {
        background-color: #0e1117;
        color: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #1f77b4;
        margin-bottom: 25px;
    }
    .match-score {
        font-size: 48px;
        font-weight: bold;
        color: #2ecc71;
        text-align: center;
    }
    .keyword-tag {
        background-color: #1f77b4;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        display: inline-block;
        margin: 4px;
        font-size: 12px;
    }
    .enhancv-sidebar {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(uploaded_file):
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "".join([page.get_text() for page in doc])
    except: return ""

# Sidebar
with st.sidebar:
    st.title("💎 Adapta-CV Pro")
    
    st.markdown("### ✨ Mejorar Texto")
    with st.container():
        st.markdown('<div class="enhancv-sidebar">', unsafe_allow_html=True)
        sug_pers = st.toggle("Sugerencias personalizadas", value=True)
        corr_orto = st.toggle("Corrector ortográfico 🔒", value=True)
        red_leg = st.toggle("Redacción y legibilidad 🔒", value=True)
        recom = st.toggle("Recomendaciones 🔒", value=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎨 Seleccionar una Plantilla")
    
    template_cat = st.selectbox("Categoría:", ["Una columna (ATS)", "Visuales / Diseño"])
    
    if template_cat == "Una columna (ATS)":
        template = st.selectbox("Plantilla:", 
                               ["Clásico", "Ivy League", "Compacto", "Alto rendimiento", "Minimalista", "Multicolumna"])
    else:
        template = st.selectbox("Plantilla:", 
                               ["Moderno", "Elegante", "Pulido", "Contemporáneo", "Creativo", "Línea de tiempo", "Estilizado"])
    
    st.markdown("---")
    provider = st.radio("Motor de IA:", ["groq", "deepseek"])
    api_key = st.secrets.get(f"{provider.upper()}_API_KEY", "")
    language = st.selectbox("Idioma:", ["es", "en"], format_func=lambda x: "Español" if x=="es" else "English")

st.title("🚀 Adapta-CV: Generador Pro")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Tu Perfil")
    uploaded_file = st.file_uploader("Sube tu CV actual (PDF)", type="pdf")
    cv_manual = st.text_area("O pega tu texto aquí:", height=150)
    cv_text = extract_text_from_pdf(uploaded_file) if uploaded_file else cv_manual

with col2:
    st.subheader("2️⃣ La Vacante")
    job_url = st.text_input("🔗 URL del empleo (LinkedIn, etc):")
    job_manual = st.text_area("O descripción manual:", height=150)

st.markdown("---")

if st.button("🔥 ACTUALIZAR PARA VER ERRORES Y GENERAR", type="primary", use_container_width=True):
    final_job_text = job_manual
    if job_url and not final_job_text:
        with st.spinner("Extrayendo descripción de la URL..."):
            try:
                optimizer_temp = CVOptimizer(provider=provider, api_key=api_key)
                final_job_text = optimizer_temp.extract_job_from_url(job_url)
            except: pass

    if not api_key or not cv_text or not final_job_text:
        st.error("Faltan datos o API Key.")
    else:
        optimizer = CVOptimizer(provider=provider, api_key=api_key)
        with st.spinner("Analizando con IA..."):
            try:
                st.session_state.analysis = optimizer.analyze_ats(cv_text, final_job_text, language)
                st.session_state.cv = optimizer.optimize_cv(cv_text, final_job_text, language)
                st.session_state.cl = optimizer.generate_cover_letter(cv_text, final_job_text, language)
            except Exception as e:
                st.error(f"Error durante el procesamiento: {e}")

# Resultados
if "analysis" in st.session_state:
    ana = st.session_state.analysis
    st.markdown(f'<div class="match-box"><div class="match-score">{ana.match_score}%</div><p style="text-align: center;">Puntaje de Coincidencia</p></div>', unsafe_allow_html=True)
    st.progress(ana.match_score / 100)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔍 Palabras Clave")
        for kw in ana.missing_keywords: st.markdown(f'<span class="keyword-tag">{kw}</span>', unsafe_allow_html=True)
    with c2:
        st.markdown("### ✨ Sugerencias")
        for sug in ana.suggestions: st.write(f"✅ {sug}")

if "cv" in st.session_state:
    st.markdown("---")
    st.subheader("📥 Descargar Documentos Pro")
    col_cv, col_cl = st.columns(2)
    with col_cv:
        st.info(f"📄 CV - Estilo {template}")
        st.download_button("Descargar Word", DocumentGenerator.generate_word(st.session_state.cv, template), f"CV_{template}.docx", use_container_width=True)
        st.download_button("Descargar PDF", DocumentGenerator.generate_pdf(st.session_state.cv, template), f"CV_{template}.pdf", use_container_width=True)
    with col_cl:
        st.info("✉️ Carta de Presentación")
        st.download_button("Descargar Word ", DocumentGenerator.generate_cl_word(st.session_state.cl, st.session_state.cv.full_name, template), "Carta.docx", use_container_width=True)
        st.download_button("PDF ", DocumentGenerator.generate_cl_pdf(st.session_state.cl, st.session_state.cv.full_name, template), "Carta.pdf", use_container_width=True)
