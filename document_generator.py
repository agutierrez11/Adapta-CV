"""
Módulo para generar documentos Word y PDF a partir de CV optimizado.
Genera formatos ATS-friendly con una sola columna.
"""

import io
from pathlib import Path
from typing import Optional
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from jinja2 import Template
from weasyprint import HTML, CSS
from llm_processor import OptimizedCV


class DocumentGenerator:
    """Generador de documentos Word y PDF para CVs optimizados"""
    
    # Estilos ATS-friendly
    FONT_NAME = "Calibri"
    FONT_SIZE_BODY = 11
    FONT_SIZE_HEADING = 12
    FONT_SIZE_NAME = 16
    MARGIN_INCHES = 0.75
    LINE_SPACING = 1.0
    
    @staticmethod
    def generate_word(cv: OptimizedCV, output_path: Optional[str] = None) -> bytes:
        """
        Genera un archivo Word (.docx) ATS-friendly.
        
        Args:
            cv: Objeto OptimizedCV con los datos del CV
            output_path: Ruta donde guardar el archivo (opcional)
        
        Returns:
            bytes: Contenido del archivo Word
        """
        doc = Document()
        
        # Configurar márgenes
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(DocumentGenerator.MARGIN_INCHES)
            section.bottom_margin = Inches(DocumentGenerator.MARGIN_INCHES)
            section.left_margin = Inches(DocumentGenerator.MARGIN_INCHES)
            section.right_margin = Inches(DocumentGenerator.MARGIN_INCHES)
        
        # Nombre
        name_para = doc.add_paragraph()
        name_run = name_para.add_run(cv.full_name)
        name_run.font.size = Pt(DocumentGenerator.FONT_SIZE_NAME)
        name_run.font.bold = True
        name_run.font.name = DocumentGenerator.FONT_NAME
        name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Información de contacto
        contact_info = []
        if cv.email:
            contact_info.append(cv.email)
        if cv.phone:
            contact_info.append(cv.phone)
        if cv.location:
            contact_info.append(cv.location)
        
        if contact_info:
            contact_para = doc.add_paragraph(" | ".join(contact_info))
            contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in contact_para.runs:
                run.font.size = Pt(DocumentGenerator.FONT_SIZE_BODY)
                run.font.name = DocumentGenerator.FONT_NAME
        
        doc.add_paragraph()  # Espacio en blanco
        
        # Resumen profesional
        if cv.professional_summary:
            summary_heading = doc.add_paragraph("PROFESSIONAL SUMMARY")
            summary_heading.runs[0].font.bold = True
            summary_heading.runs[0].font.size = Pt(DocumentGenerator.FONT_SIZE_HEADING)
            summary_heading.runs[0].font.name = DocumentGenerator.FONT_NAME
            
            summary_para = doc.add_paragraph(cv.professional_summary)
            for run in summary_para.runs:
                run.font.size = Pt(DocumentGenerator.FONT_SIZE_BODY)
                run.font.name = DocumentGenerator.FONT_NAME
            doc.add_paragraph()
        
        # Habilidades clave
        if cv.key_skills:
            skills_heading = doc.add_paragraph("KEY SKILLS")
            skills_heading.runs[0].font.bold = True
            skills_heading.runs[0].font.size = Pt(DocumentGenerator.FONT_SIZE_HEADING)
            skills_heading.runs[0].font.name = DocumentGenerator.FONT_NAME
            
            skills_para = doc.add_paragraph(", ".join(cv.key_skills))
            for run in skills_para.runs:
                run.font.size = Pt(DocumentGenerator.FONT_SIZE_BODY)
                run.font.name = DocumentGenerator.FONT_NAME
            doc.add_paragraph()
        
        # Experiencia laboral
        if cv.experience:
            exp_heading = doc.add_paragraph("PROFESSIONAL EXPERIENCE")
            exp_heading.runs[0].font.bold = True
            exp_heading.runs[0].font.size = Pt(DocumentGenerator.FONT_SIZE_HEADING)
            exp_heading.runs[0].font.name = DocumentGenerator.FONT_NAME
            
            for exp in cv.experience:
                # Título y empresa
                job_para = doc.add_paragraph()
                job_run = job_para.add_run(f"{exp.job_title} | {exp.company}")
                job_run.font.bold = True
                job_run.font.size = Pt(DocumentGenerator.FONT_SIZE_BODY)
                job_run.font.name = DocumentGenerator.FONT_NAME
                
                # Duración
                duration_para = doc.add_paragraph(exp.duration)
                for run in duration_para.runs:
                    run.font.size = Pt(DocumentGenerator.FONT_SIZE_BODY - 1)
                    run.font.name = DocumentGenerator.FONT_NAME
                    run.font.italic = True
                
                # Logros
                for achievement in exp.achievements:
                    achievement_para = doc.add_paragraph(achievement, style='List Bullet')
                    for run in achievement_para.runs:
                        run.font.size = Pt(DocumentGenerator.FONT_SIZE_BODY)
                        run.font.name = DocumentGenerator.FONT_NAME
            
            doc.add_paragraph()
        
        # Educación
        if cv.education:
            edu_heading = doc.add_paragraph("EDUCATION")
            edu_heading.runs[0].font.bold = True
            edu_heading.runs[0].font.size = Pt(DocumentGenerator.FONT_SIZE_HEADING)
            edu_heading.runs[0].font.name = DocumentGenerator.FONT_NAME
            
            for edu in cv.education:
                edu_para = doc.add_paragraph()
                degree_run = edu_para.add_run(f"{edu.degree} | {edu.institution}")
                degree_run.font.bold = True
                degree_run.font.size = Pt(DocumentGenerator.FONT_SIZE_BODY)
                degree_run.font.name = DocumentGenerator.FONT_NAME
                
                year_para = doc.add_paragraph(f"Graduated: {edu.year}")
                for run in year_para.runs:
                    run.font.size = Pt(DocumentGenerator.FONT_SIZE_BODY - 1)
                    run.font.name = DocumentGenerator.FONT_NAME
                    run.font.italic = True
            
            doc.add_paragraph()
        
        # Idiomas
        if cv.languages:
            lang_heading = doc.add_paragraph("LANGUAGES")
            lang_heading.runs[0].font.bold = True
            lang_heading.runs[0].font.size = Pt(DocumentGenerator.FONT_SIZE_HEADING)
            lang_heading.runs[0].font.name = DocumentGenerator.FONT_NAME
            
            lang_para = doc.add_paragraph(", ".join(cv.languages))
            for run in lang_para.runs:
                run.font.size = Pt(DocumentGenerator.FONT_SIZE_BODY)
                run.font.name = DocumentGenerator.FONT_NAME
            doc.add_paragraph()
        
        # Certificaciones
        if cv.certifications:
            cert_heading = doc.add_paragraph("CERTIFICATIONS")
            cert_heading.runs[0].font.bold = True
            cert_heading.runs[0].font.size = Pt(DocumentGenerator.FONT_SIZE_HEADING)
            cert_heading.runs[0].font.name = DocumentGenerator.FONT_NAME
            
            for cert in cv.certifications:
                cert_para = doc.add_paragraph(cert, style='List Bullet')
                for run in cert_para.runs:
                    run.font.size = Pt(DocumentGenerator.FONT_SIZE_BODY)
                    run.font.name = DocumentGenerator.FONT_NAME
        
        # Guardar o retornar bytes
        if output_path:
            doc.save(output_path)
            with open(output_path, 'rb') as f:
                return f.read()
        else:
            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            return buffer.getvalue()
    
    @staticmethod
    def generate_pdf(cv: OptimizedCV, output_path: Optional[str] = None) -> bytes:
        """
        Genera un archivo PDF ATS-friendly usando HTML + CSS.
        
        Args:
            cv: Objeto OptimizedCV con los datos del CV
            output_path: Ruta donde guardar el archivo (opcional)
        
        Returns:
            bytes: Contenido del archivo PDF
        """
        html_content = DocumentGenerator._generate_html(cv)
        
        # Crear HTML
        html_obj = HTML(string=html_content)
        
        # CSS para ATS-friendly
        css_str = """
        @page {
            margin: 0.75in;
            size: letter;
        }
        body {
            font-family: Calibri, Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.0;
            color: #000;
        }
        h1 {
            font-size: 16pt;
            font-weight: bold;
            text-align: center;
            margin: 0 0 5pt 0;
        }
        .contact-info {
            text-align: center;
            font-size: 10pt;
            margin-bottom: 10pt;
        }
        h2 {
            font-size: 12pt;
            font-weight: bold;
            margin: 10pt 0 5pt 0;
            border-bottom: 1px solid #000;
            padding-bottom: 2pt;
        }
        .job-title {
            font-weight: bold;
            font-size: 11pt;
            margin: 5pt 0 2pt 0;
        }
        .company {
            font-style: italic;
            font-size: 10pt;
            margin: 0 0 3pt 0;
        }
        ul {
            margin: 3pt 0 5pt 20pt;
            padding: 0;
        }
        li {
            margin: 2pt 0;
            font-size: 11pt;
        }
        .skills {
            margin: 5pt 0;
            font-size: 11pt;
        }
        """
        
        css_obj = CSS(string=css_str)
        
        # Generar PDF
        if output_path:
            html_obj.write_pdf(output_path, stylesheets=[css_obj])
            with open(output_path, 'rb') as f:
                return f.read()
        else:
            buffer = io.BytesIO()
            html_obj.write_pdf(buffer, stylesheets=[css_obj])
            buffer.seek(0)
            return buffer.getvalue()
    
    @staticmethod
    def _generate_html(cv: OptimizedCV) -> str:
        """Genera el HTML para el PDF"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ full_name }} - Resume</title>
</head>
<body>
    <h1>{{ full_name }}</h1>
    
    <div class="contact-info">
        {% if email %}{{ email }}{% endif %}
        {% if phone %} | {{ phone }}{% endif %}
        {% if location %} | {{ location }}{% endif %}
    </div>
    
    {% if professional_summary %}
    <h2>PROFESSIONAL SUMMARY</h2>
    <p>{{ professional_summary }}</p>
    {% endif %}
    
    {% if key_skills %}
    <h2>KEY SKILLS</h2>
    <div class="skills">{{ key_skills_str }}</div>
    {% endif %}
    
    {% if experience %}
    <h2>PROFESSIONAL EXPERIENCE</h2>
    {% for exp in experience %}
        <div class="job-title">{{ exp.job_title }} | {{ exp.company }}</div>
        <div class="company">{{ exp.duration }}</div>
        <ul>
        {% for achievement in exp.achievements %}
            <li>{{ achievement }}</li>
        {% endfor %}
        </ul>
    {% endfor %}
    {% endif %}
    
    {% if education %}
    <h2>EDUCATION</h2>
    {% for edu in education %}
        <div class="job-title">{{ edu.degree }} | {{ edu.institution }}</div>
        <div class="company">Graduated: {{ edu.year }}</div>
    {% endfor %}
    {% endif %}
    
    {% if languages %}
    <h2>LANGUAGES</h2>
    <div class="skills">{{ languages_str }}</div>
    {% endif %}
    
    {% if certifications %}
    <h2>CERTIFICATIONS</h2>
    <ul>
    {% for cert in certifications %}
        <li>{{ cert }}</li>
    {% endfor %}
    </ul>
    {% endif %}
    
</body>
</html>
        """
        
        template = Template(html_template)
        html = template.render(
            full_name=cv.full_name,
            email=cv.email,
            phone=cv.phone,
            location=cv.location,
            professional_summary=cv.professional_summary,
            key_skills=cv.key_skills,
            key_skills_str=", ".join(cv.key_skills),
            experience=cv.experience,
            education=cv.education,
            languages=cv.languages,
            languages_str=", ".join(cv.languages),
            certifications=cv.certifications
        )
        
        return html
