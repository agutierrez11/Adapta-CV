import streamlit as st
import os
import fitz
import pandas as pd
from llm_processor import CVOptimizer
from document_generator import DocumentGenerator

st.set_page_config(page_title="Adapta-CV Pro & Job Finder", page_icon="🚀", layout="wide")

# Estilos Pro
st.markdown("""
<style>
    .main-header { text-align: center; color: #1f77b4; margin-bottom: 20px; }
    .match-box {
        background-color: #0e1117; color: white; padding: 25px; border-radius: 15px;
        border: 1px solid #1f77b4; margin-bottom: 25px;
    }
    .match-score { font-size: 48px; font-weight: bold; color: #2ecc71; text-align: center; }
    .keyword-tag {
        background-color: #1f77b4; color: white; padding: 4px 10px; border-radius: 20px;
        display: inline-block; margin: 4px; font-size: 12px;
    }
    .job-card {
        background-color: white; padding: 15px; border-radius: 10px;
        border: 1px solid #e0e0e0; margin-bottom: 10px;
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
    sug_pers = st.toggle("Sugerencias personalizadas", value=True)
    corr_orto = st.toggle("Corrector ortográfico 🔒", value=True)
    
    st.markdown("---")
    st.markdown("### 🎨 Plantilla")
    template_cat = st.selectbox("Categoría:", ["Una columna (ATS)", "Visuales / Diseño"])
    if template_cat == "Una columna (ATS)":
        template = st.selectbox("Plantilla:", ["Clásico", "Ivy League", "Compacto", "Alto rendimiento", "Minimalista"])
    else:
        template = st.selectbox("Plantilla:", ["Moderno", "Elegante", "Pulido", "Contemporáneo", "Creativo", "Línea de tiempo", "Estilizado"])
    
    st.markdown("---")
    provider = st.radio("Motor de IA:", ["groq", "deepseek"])
    api_key = st.secrets.get(f"{provider.upper()}_API_KEY", "")
    language = st.selectbox("Idioma:", ["es", "en"], format_func=lambda x: "Español" if x=="es" else "English")

st.title("🚀 Adapta-CV: Job Finder & Optimizer")

# --- SECCIÓN DE BÚSQUEDA DE EMPLEO ---
st.markdown("### 🔍 Buscador Activo de Vacantes")
with st.container():
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        search_query = st.text_input("Puesto (ej: Software Engineer)", placeholder="¿Qué buscas?")
    with c2:
        search_location = st.text_input("Ubicación (ej: Spain, Remote)", placeholder="¿Dónde?")
    with c3:
        st.write(" ")
        search_btn = st.button("Buscar Empleos", use_container_width=True)

if search_btn and search_query:
    with st.spinner("Buscando vacantes en LinkedIn, Indeed y más..."):
        optimizer = CVOptimizer(provider=provider, api_key=api_key)
        df_jobs = optimizer.search_jobs(search_query, search_location)
        if not df_jobs.empty:
            st.session_state.jobs_list = df_jobs
        else:
            st.warning("No se encontraron resultados. Intenta con otros términos.")

if "jobs_list" in st.session_state:
    st.write("---")
    st.write("##### 📋 Resultados encontrados (Selecciona uno para optimizar tu CV):")
    for index, row in st.session_state.jobs_list.iterrows():
        with st.container():
            col_info, col_act = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{row['title']}** - {row['company']} ({row['location']}) | *Fuente: {row['site']}*")
            with col_act:
                if st.button("Usar esta vacante", key=f"btn_{index}"):
                    st.session_state.selected_url = row['job_url']
                    st.success(f"URL seleccionada: {row['title']}")
    st.write("---")

# --- SECCIÓN DE OPTIMIZACIÓN ---
col_cv, col_job = st.columns(2)

with col_cv:
    st.subheader("1️⃣ Tu Perfil")
    uploaded_file = st.file_uploader("Sube tu CV (PDF)", type="pdf")
    cv_manual = st.text_area("O pega tu texto aquí:", height=200)
    cv_text = extract_text_from_pdf(uploaded_file) if uploaded_file else cv_manual

with col_job:
    st.subheader("2️⃣ La Vacante")
    current_url = st.text_input("🔗 URL de la vacante:", value=st.session_state.get("selected_url", ""))
    job_manual = st.text_area("Descripción (se llenará automáticamente al procesar):", height=200)

if st.button("🔥 ANALIZAR Y GENERAR TODO", type="primary", use_container_width=True):
    final_job_text = job_manual
    if current_url and not final_job_text:
        with st.spinner("Extrayendo contenido de la vacante..."):
            try:
                opt = CVOptimizer(provider=provider, api_key=api_key)
                final_job_text = opt.extract_job_from_url(current_url)
            except: pass

    if not api_key or not cv_text or not final_job_text:
        st.error("Faltan datos o configuración de API Key.")
    else:
        optimizer = CVOptimizer(provider=provider, api_key=api_key)
        with st.spinner("Procesando con IA..."):
            try:
                st.session_state.analysis = optimizer.analyze_ats(cv_text, final_job_text, language)
                st.session_state.cv = optimizer.optimize_cv(cv_text, final_job_text, language)
                st.session_state.cl = optimizer.generate_cover_letter(cv_text, final_job_text, language)
            except Exception as e:
                st.error(f"Error: {e}")

# --- RESULTADOS Y DESCARGAS ---
if "analysis" in st.session_state:
    ana = st.session_state.analysis
    st.markdown(f'<div class="match-box"><div class="match-score">{ana.match_score}%</div><p style="text-align: center;">Match Score ATS</p></div>', unsafe_allow_html=True)
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
    st.subheader("📥 Descargar Documentos")
    col_cv_dl, col_cl_dl = st.columns(2)
    with col_cv_dl:
        st.info(f"📄 CV - {template}")
        st.download_button("Descargar Word", DocumentGenerator.generate_word(st.session_state.cv, template), f"CV_{template}.docx", use_container_width=True)
        st.download_button("Descargar PDF", DocumentGenerator.generate_pdf(st.session_state.cv, template), f"CV_{template}.pdf", use_container_width=True)
    with col_cl_dl:
        st.info("✉️ Carta de Presentación")
        st.download_button("Descargar Word ", DocumentGenerator.generate_cl_word(st.session_state.cl, st.session_state.cv.full_name, template), "Carta.docx", use_container_width=True)
        st.download_button("PDF ", DocumentGenerator.generate_cl_pdf(st.session_state.cl, st.session_state.cv.full_name, template), "Carta.pdf", use_container_width=True)
