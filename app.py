"""
Aplicación Streamlit para optimización de CV con ATS.
Interfaz web para generar CVs optimizados en Word y PDF.
"""

import os
import io
import streamlit as st
from datetime import datetime
from llm_processor import CVOptimizer, OptimizedCV
from document_generator import DocumentGenerator


# Configuración de la página
st.set_page_config(
    page_title="CV Optimizer ATS",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
        margin-top: 20px;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar sesión
if "cv_optimizer" not in st.session_state:
    try:
        st.session_state.cv_optimizer = CVOptimizer()
        st.session_state.optimizer_ready = True
    except ValueError as e:
        st.session_state.optimizer_ready = False
        st.session_state.optimizer_error = str(e)

if "optimized_cv" not in st.session_state:
    st.session_state.optimized_cv = None

if "cv_text" not in st.session_state:
    st.session_state.cv_text = ""


def main():
    """Función principal de la aplicación"""
    
    # Header
    st.markdown("<h1 class='main-header'>📄 CV Optimizer for ATS</h1>", unsafe_allow_html=True)
    st.markdown("""
    Optimize your resume to pass Applicant Tracking Systems (ATS) while maintaining authenticity.
    This tool analyzes your CV and job description to create a perfectly aligned resume.
    """)
    
    # Verificar si el optimizador está listo
    if not st.session_state.optimizer_ready:
        st.error(f"""
        ❌ Error initializing the optimizer:
        
        {st.session_state.optimizer_error}
        
        **Solution:** Please set your DeepSeek API key in one of these ways:
        1. Create a `.env` file in the project folder with: `DEEPSEEK_API_KEY=your_key_here`
        2. Set the environment variable: `export DEEPSEEK_API_KEY=your_key_here`
        3. Pass it directly in the code
        """)
        return
    
    # Sidebar para configuración
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        language = st.selectbox(
            "Select output language:",
            options=["es", "en"],
            format_func=lambda x: "🇪🇸 Español" if x == "es" else "🇬🇧 English"
        )
        
        st.markdown("---")
        st.markdown("### 📋 About this tool")
        st.info("""
        This tool uses **DeepSeek API** to:
        - Analyze your current CV
        - Extract keywords from the job description
        - Rewrite your experience to align with the job
        - Generate ATS-optimized documents
        
        **Important:** No information is invented. Only your real experience is reframed.
        """)
    
    # Columnas principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 class='section-header'>📝 Step 1: Your CV</h3>", unsafe_allow_html=True)
        st.markdown("""
        Paste your current CV text here. You can copy from:
        - A Word document
        - A PDF (copy-paste the text)
        - Your LinkedIn profile
        """)
        
        cv_input = st.text_area(
            "Paste your CV text:",
            height=250,
            key="cv_input",
            placeholder="Paste your CV content here..."
        )
        
        if cv_input:
            st.session_state.cv_text = cv_input
    
    with col2:
        st.markdown("<h3 class='section-header'>💼 Step 2: Job Description</h3>", unsafe_allow_html=True)
        st.markdown("""
        Paste the job description you're applying for.
        The tool will extract keywords and align your CV.
        """)
        
        job_input = st.text_area(
            "Paste the job description:",
            height=250,
            key="job_input",
            placeholder="Paste the job description here..."
        )
    
    # Botón de procesamiento
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        process_button = st.button(
            "🚀 Optimize CV",
            key="process_btn",
            use_container_width=True,
            type="primary"
        )
    
    # Procesar CV
    if process_button:
        if not st.session_state.cv_text or not job_input:
            st.error("❌ Please fill in both fields: your CV and the job description.")
        else:
            with st.spinner("🔄 Optimizing your CV..."):
                try:
                    # Llamar al optimizador
                    optimized_cv = st.session_state.cv_optimizer.optimize_cv(
                        cv_text=st.session_state.cv_text,
                        job_description=job_input,
                        language=language
                    )
                    
                    st.session_state.optimized_cv = optimized_cv
                    st.success("✅ CV optimized successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error optimizing CV: {str(e)}")
    
    # Mostrar CV optimizado
    if st.session_state.optimized_cv:
        st.markdown("---")
        st.markdown("<h3 class='section-header'>✨ Your Optimized CV</h3>", unsafe_allow_html=True)
        
        cv = st.session_state.optimized_cv
        
        # Mostrar preview
        with st.expander("👁️ Preview of optimized CV", expanded=True):
            col_preview1, col_preview2 = st.columns(2)
            
            with col_preview1:
                st.markdown("**Name:**")
                st.write(cv.full_name)
                
                st.markdown("**Contact:**")
                contact = []
                if cv.email:
                    contact.append(cv.email)
                if cv.phone:
                    contact.append(cv.phone)
                if cv.location:
                    contact.append(cv.location)
                st.write(" | ".join(contact))
                
                st.markdown("**Professional Summary:**")
                st.write(cv.professional_summary)
            
            with col_preview2:
                st.markdown("**Key Skills:**")
                st.write(", ".join(cv.key_skills))
                
                st.markdown("**Languages:**")
                st.write(", ".join(cv.languages))
                
                if cv.certifications:
                    st.markdown("**Certifications:**")
                    for cert in cv.certifications:
                        st.write(f"• {cert}")
            
            st.markdown("**Experience:**")
            for exp in cv.experience:
                st.markdown(f"**{exp.job_title}** | {exp.company}")
                st.markdown(f"*{exp.duration}*")
                for achievement in exp.achievements:
                    st.write(f"• {achievement}")
                st.write("")
            
            st.markdown("**Education:**")
            for edu in cv.education:
                st.markdown(f"**{edu.degree}** | {edu.institution}")
                st.write(f"Graduated: {edu.year}")
        
        # Descargas
        st.markdown("---")
        st.markdown("<h3 class='section-header'>📥 Download Your CV</h3>", unsafe_allow_html=True)
        
        col_down1, col_down2 = st.columns(2)
        
        with col_down1:
            # Generar Word
            try:
                word_bytes = DocumentGenerator.generate_word(cv)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename_word = f"CV_Optimized_{timestamp}.docx"
                
                st.download_button(
                    label="📄 Download as Word (.docx)",
                    data=word_bytes,
                    file_name=filename_word,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating Word document: {str(e)}")
        
        with col_down2:
            # Generar PDF
            try:
                pdf_bytes = DocumentGenerator.generate_pdf(cv)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename_pdf = f"CV_Optimized_{timestamp}.pdf"
                
                st.download_button(
                    label="📕 Download as PDF",
                    data=pdf_bytes,
                    file_name=filename_pdf,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
        
        st.markdown("""
        <div class='info-box'>
        <strong>💡 Tips for best results:</strong>
        <ul>
        <li>Upload the Word document first to job portals</li>
        <li>Use the PDF for email submissions</li>
        <li>Both formats are ATS-optimized with single-column layout</li>
        <li>Fonts and spacing follow ATS best practices</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
