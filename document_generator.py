"""
Módulo para generar documentos Word y PDF a partir de CV optimizado.
Genera formatos ATS-friendly con estilos personalizables (Clásico, Moderno, Minimalista).
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
    
    @staticmethod
    def generate_word(cv: OptimizedCV, template: str = "Clásico", output_path: Optional[str] = None) -> bytes:
        """
        Genera un archivo Word (.docx) ATS-friendly con la plantilla seleccionada.
        """
        doc = Document()
        
        # Configurar estilos de plantilla
        template_lower = template.lower()
        if "modern" in template_lower:
            font_name = "Arial"
            font_size_name = 18
            font_size_heading = 13
            font_size_body = 11
            color_heading = RGBColor(31, 119, 180)  # #1f77b4
            margin_inches = 0.75
            align_name = WD_ALIGN_PARAGRAPH.LEFT
        elif "minim" in template_lower:
            font_name = "Georgia"
            font_size_name = 16
            font_size_heading = 11
            font_size_body = 10.5
            color_heading = RGBColor(80, 80, 80)  # Gris carbón
            margin_inches = 1.0
            align_name = WD_ALIGN_PARAGRAPH.CENTER
        else:  # Clásico
            font_name = "Calibri"
            font_size_name = 16
            font_size_heading = 12
            font_size_body = 11
            color_heading = RGBColor(0, 0, 0)  # Negro
            margin_inches = 0.75
            align_name = WD_ALIGN_PARAGRAPH.CENTER
            
        # Configurar márgenes
        for section in doc.sections:
            section.top_margin = Inches(margin_inches)
            section.bottom_margin = Inches(margin_inches)
            section.left_margin = Inches(margin_inches)
            section.right_margin = Inches(margin_inches)
        
        # Helper para agregar párrafos con formato uniforme
        def add_formatted_para(text="", font_size=font_size_body, bold=False, italic=False, color=None, style='Normal', align=WD_ALIGN_PARAGRAPH.LEFT):
            para = doc.add_paragraph(style=style)
            para.alignment = align
            if text:
                run = para.add_run(text)
                run.font.name = font_name
                run.font.size = Pt(font_size)
                run.font.bold = bold
                run.font.italic = italic
                if color:
                    run.font.color.rgb = color
            return para

        # Helper para agregar textos en el mismo párrafo con diferentes formatos
        def add_run_to_para(para, text, font_size=font_size_body, bold=False, italic=False, color=None):
            run = para.add_run(text)
            run.font.name = font_name
            run.font.size = Pt(font_size)
            run.font.bold = bold
            run.font.italic = italic
            if color:
                run.font.color.rgb = color
            return run

        # Nombre completo
        add_formatted_para(cv.full_name, font_size=font_size_name, bold=True, color=color_heading, align=align_name)
        
        # Información de contacto
        contact_info = []
        if cv.email:
            contact_info.append(cv.email)
        if cv.phone:
            contact_info.append(cv.phone)
        if cv.location:
            contact_info.append(cv.location)
        
        if contact_info:
            add_formatted_para(" | ".join(contact_info), font_size=font_size_body - 1, align=align_name)
        
        doc.add_paragraph()  # Espacio en blanco
        
        # Resumen profesional
        if cv.professional_summary:
            add_formatted_para("PROFESSIONAL SUMMARY", font_size=font_size_heading, bold=True, color=color_heading)
            add_formatted_para(cv.professional_summary, font_size=font_size_body)
            doc.add_paragraph()
        
        # Habilidades clave
        if cv.key_skills:
            add_formatted_para("KEY SKILLS", font_size=font_size_heading, bold=True, color=color_heading)
            add_formatted_para(", ".join(cv.key_skills), font_size=font_size_body)
            doc.add_paragraph()
        
        # Experiencia laboral
        if cv.experience:
            add_formatted_para("PROFESSIONAL EXPERIENCE", font_size=font_size_heading, bold=True, color=color_heading)
            for exp in cv.experience:
                # Puesto y Empresa
                job_para = add_formatted_para()
                add_run_to_para(job_para, f"{exp.job_title} | {exp.company}", font_size=font_size_body, bold=True)
                
                # Duración
                dur_para = add_formatted_para()
                add_run_to_para(dur_para, exp.duration, font_size=font_size_body - 1, italic=True)
                
                # Logros
                for achievement in exp.achievements:
                    ach_para = doc.add_paragraph(style='List Bullet')
                    add_run_to_para(ach_para, achievement, font_size=font_size_body)
            doc.add_paragraph()
        
        # Educación
        if cv.education:
            add_formatted_para("EDUCATION", font_size=font_size_heading, bold=True, color=color_heading)
            for edu in cv.education:
                edu_para = add_formatted_para()
                add_run_to_para(edu_para, f"{edu.degree} | {edu.institution}", font_size=font_size_body, bold=True)
                
                year_para = add_formatted_para()
                add_run_to_para(year_para, f"Graduated: {edu.year}", font_size=font_size_body - 1, italic=True)
            doc.add_paragraph()
        
        # Idiomas
        if cv.languages:
            add_formatted_para("LANGUAGES", font_size=font_size_heading, bold=True, color=color_heading)
            add_formatted_para(", ".join(cv.languages), font_size=font_size_body)
            doc.add_paragraph()
        
        # Certificaciones
        if cv.certifications:
            add_formatted_para("CERTIFICATIONS", font_size=font_size_heading, bold=True, color=color_heading)
            for cert in cv.certifications:
                cert_para = doc.add_paragraph(style='List Bullet')
                add_run_to_para(cert_para, cert, font_size=font_size_body)
        
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
    def generate_pdf(cv: OptimizedCV, template: str = "Clásico", output_path: Optional[str] = None) -> bytes:
        """
        Genera un archivo PDF ATS-friendly usando HTML + CSS adaptado a la plantilla.
        """
        html_content = DocumentGenerator._generate_html(cv)
        html_obj = HTML(string=html_content)
        
        template_lower = template.lower()
        if "modern" in template_lower:
            css_str = """
            @page {
                margin: 0.75in;
                size: letter;
            }
            body {
                font-family: Arial, Helvetica, sans-serif;
                font-size: 11pt;
                line-height: 1.15;
                color: #222;
            }
            h1 {
                font-size: 18pt;
                font-weight: bold;
                color: #1f77b4;
                text-align: left;
                margin: 0 0 5pt 0;
            }
            .contact-info {
                text-align: left;
                font-size: 10pt;
                color: #555;
                margin-bottom: 12pt;
            }
            h2 {
                font-size: 13pt;
                font-weight: bold;
                color: #1f77b4;
                margin: 15pt 0 6pt 0;
                border-bottom: 2px solid #1f77b4;
                padding-bottom: 3pt;
                text-transform: uppercase;
            }
            .job-title {
                font-weight: bold;
                font-size: 11pt;
                margin: 6pt 0 1pt 0;
            }
            .company {
                font-style: italic;
                font-size: 10pt;
                color: #555;
                margin: 0 0 4pt 0;
            }
            ul {
                margin: 2pt 0 6pt 15pt;
                padding: 0;
            }
            li {
                margin: 2pt 0;
                font-size: 10.5pt;
            }
            .skills {
                margin: 4pt 0;
                font-size: 11pt;
            }
            """
        elif "minim" in template_lower:
            css_str = """
            @page {
                margin: 1.0in;
                size: letter;
            }
            body {
                font-family: Georgia, serif;
                font-size: 10.5pt;
                line-height: 1.2;
                color: #333;
            }
            h1 {
                font-size: 16pt;
                font-weight: normal;
                color: #000;
                text-align: center;
                margin: 0 0 5pt 0;
                letter-spacing: 0.05em;
            }
            .contact-info {
                text-align: center;
                font-size: 9.5pt;
                color: #666;
                margin-bottom: 15pt;
            }
            h2 {
                font-size: 11pt;
                font-weight: bold;
                color: #555;
                margin: 18pt 0 8pt 0;
                text-align: center;
                letter-spacing: 0.1em;
                text-transform: uppercase;
                border-bottom: none;
            }
            .job-title {
                font-weight: bold;
                font-size: 10.5pt;
                margin: 8pt 0 1pt 0;
            }
            .company {
                font-style: italic;
                font-size: 9.5pt;
                color: #666;
                margin: 0 0 4pt 0;
            }
            ul {
                margin: 3pt 0 6pt 12pt;
                padding: 0;
            }
            li {
                margin: 3pt 0;
                font-size: 10.5pt;
            }
            .skills {
                margin: 5pt 0;
                font-size: 10.5pt;
                text-align: justify;
            }
            """
        else:  # Clásico
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
        """Genera el HTML base para el PDF"""
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
