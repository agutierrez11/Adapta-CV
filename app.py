import streamlit as st
import os
import pypdf
from llm_processor import CVOptimizer
from document_generator import DocumentGenerator

st.set_page_config(page_title="Adapta-CV Pro", page_icon="🚀", layout="wide")

# Estilos personalizados para simular la interfaz de la imagen
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
    .stProgress > div > div > div > div {
        background-color: #2ecc71;
    }
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
    st.title("🛠️ Adapta-CV Pro")
    provider = st.radio("Motor de IA:", ["groq", "deepseek"])
    
    # Obtener API Key de Secrets directamente para mantener la UI limpia e invulnerable
    api_key = st.secrets.get(f"{provider.upper()}_API_KEY", "")
    
    template = st.selectbox("🎨 Diseño:", ["Clásico", "Moderno", "Minimalista"])
    language = st.selectbox("🌐 Idioma:", ["es", "en"])

st.title("🚀 Adapta-CV: ¿Pasará el ATS?")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Tu Perfil")
    uploaded_file = st.file_uploader("Sube tu CV en PDF", type="pdf")
    cv_manual = st.text_area("O pega tu texto aquí:", height=150)
    cv_text = extract_text_from_pdf(uploaded_file) if uploaded_file else cv_manual

with col2:
    st.subheader("2️⃣ La Vacante")
    job_url = st.text_input("🔗 Enlace del empleo (LinkedIn, etc):")
    job_manual = st.text_area("O descripción manual:", height=150)
    
    job_text = job_manual
    if job_url and st.button("🔍 Analizar Vacante"):
        if not api_key:
            st.error(f"Por favor configura la API Key de {provider.upper()} en los Secrets de Streamlit Cloud.")
        else:
            with st.spinner("Leyendo vacante..."):
                try:
                    optimizer = CVOptimizer(provider=provider, api_key=api_key)
                    job_text = optimizer.extract_job_from_url(job_url)
                    st.session_state.job_text = job_text
                    st.info("Contenido extraído con éxito.")
                except Exception as e:
                    st.error(f"Error al extraer la vacante: {e}")

if "job_text" in st.session_state:
    job_text = st.session_state.job_text

st.markdown("---")

# Botón Principal
if st.button("🔥 ANALIZAR Y GENERAR TODO", type="primary", use_container_width=True):
    if not api_key:
        st.error(f"Por favor configura la API Key de {provider.upper()} en los Secrets de Streamlit Cloud.")
    elif not cv_text or not job_text:
        st.error("Faltan datos (CV o descripción del empleo).")
    else:
        try:
            optimizer = CVOptimizer(provider=provider, api_key=api_key)
            
            # 1. Análisis ATS
            with st.spinner("Calculando Match Score..."):
                st.session_state.analysis = optimizer.analyze_ats(cv_text, job_text, language)
            
            # 2. Optimización CV
            with st.spinner("Optimizando CV..."):
                st.session_state.cv = optimizer.optimize_cv(cv_text, job_text, language)
                
            # 3. Carta de Presentación
            with st.spinner("Redactando Carta..."):
                st.session_state.cl = optimizer.generate_cover_letter(cv_text, job_text, language)
            
            st.success("¡Análisis y generación completados!")
        except Exception as e:
            st.error(f"Error durante el procesamiento: {e}")

# Mostrar Resultados del Análisis (Estilo de la imagen de referencia)
if "analysis" in st.session_state:
    ana = st.session_state.analysis
    
    st.markdown(f"""
    <div class="match-box">
        <h2 style='text-align: center; color: #2ecc71;'>¡Análisis Completado!</h2>
        <div class="match-score">{ana.match_score}%</div>
        <p style='text-align: center;'>Puntaje de coincidencia real con la vacante</p>
    </div>
    """, unsafe_allow_html=True)
    st.progress(ana.match_score / 100)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔍 Palabras clave faltantes")
        if ana.missing_keywords:
            for kw in ana.missing_keywords:
                st.markdown(f'<span class="keyword-tag">{kw}</span>', unsafe_allow_html=True)
        else:
            st.write("¡Ninguna! Tu CV tiene todas las palabras clave necesarias.")
            
    with c2:
        st.markdown("### ✨ Sugerencias personalizadas")
        if ana.suggestions:
            for sug in ana.suggestions:
                st.write(f"✅ {sug}")
        else:
            st.write("Tu perfil se alinea perfectamente con los requerimientos.")

# Descargas
if "cv" in st.session_state:
    st.markdown("---")
    st.subheader("📥 Descargar Archivos Optimizados")
    col_cv, col_cl = st.columns(2)
    
    with col_cv:
        st.info("📄 CV OPTIMIZADO")
        try:
            word_data = DocumentGenerator.generate_word(st.session_state.cv, template)
            pdf_data = DocumentGenerator.generate_pdf(st.session_state.cv, template)
            st.download_button("Word (.docx)", word_data, "CV_Optimizado.docx", use_container_width=True)
            st.download_button("PDF", pdf_data, "CV_Optimizado.pdf", use_container_width=True)
        except Exception as e:
            st.error(f"Error generando descargas de CV: {e}")
        
    with col_cl:
        st.info("✉️ CARTA DE PRESENTACIÓN")
        try:
            cl_word_data = DocumentGenerator.generate_cl_word(st.session_state.cl, st.session_state.cv.full_name, template)
            cl_pdf_data = DocumentGenerator.generate_cl_pdf(st.session_state.cl, st.session_state.cv.full_name, template)
            st.download_button("Word (.docx)", cl_word_data, "Carta_Presentacion.docx", use_container_width=True)
            st.download_button("PDF", cl_pdf_data, "Carta_Presentacion.pdf", use_container_width=True)
        except Exception as e:
            st.error(f"Error generando descargas de Carta: {e}")
