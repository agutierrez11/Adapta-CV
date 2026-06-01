"""
Script de prueba para verificar que la aplicación funciona correctamente.
Prueba la lógica sin necesidad de Streamlit.
"""

import os
import json
from llm_processor import CVOptimizer, OptimizedCV
from document_generator import DocumentGenerator


def test_cv_optimizer():
    """Prueba el optimizador de CV con datos de ejemplo"""
    
    print("=" * 60)
    print("Testing CV Optimizer Application")
    print("=" * 60)
    
    # Datos de prueba
    sample_cv = """
    John Smith
    john.smith@email.com
    +1 (555) 123-4567
    New York, NY
    
    PROFESSIONAL EXPERIENCE
    
    Senior Software Engineer
    Tech Company Inc.
    January 2020 - Present
    - Developed web applications using Python and JavaScript
    - Led a team of 5 developers
    - Improved system performance by 40%
    - Managed databases and APIs
    
    Junior Developer
    Startup Co.
    June 2018 - December 2019
    - Built features for mobile and web platforms
    - Worked with React and Node.js
    - Collaborated with design team
    
    EDUCATION
    
    Bachelor of Science in Computer Science
    University of Technology
    Graduated: 2018
    
    SKILLS
    Python, JavaScript, React, Node.js, SQL, Docker, AWS
    
    LANGUAGES
    English (Native), Spanish (Intermediate)
    """
    
    sample_job = """
    Senior Python Developer
    
    We are looking for an experienced Python Developer to join our growing team.
    
    Requirements:
    - 5+ years of experience with Python
    - Strong knowledge of web frameworks (Django, FastAPI)
    - Experience with SQL and NoSQL databases
    - AWS or cloud platform experience
    - Leadership experience
    - Strong problem-solving skills
    
    Responsibilities:
    - Develop and maintain Python applications
    - Design database schemas
    - Lead code reviews
    - Mentor junior developers
    - Optimize application performance
    
    Nice to have:
    - Docker and Kubernetes experience
    - Experience with microservices
    - Open source contributions
    """
    
    print("\n1. Testing CVOptimizer initialization...")
    try:
        # Verificar que la API key esté disponible
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            print("   ⚠️  DEEPSEEK_API_KEY not found in environment")
            print("   Please set it before running the app:")
            print("   export DEEPSEEK_API_KEY='your_key_here'")
            return False
        
        optimizer = CVOptimizer(api_key=api_key)
        print("   ✅ CVOptimizer initialized successfully")
    except Exception as e:
        print(f"   ❌ Error initializing CVOptimizer: {e}")
        return False
    
    print("\n2. Testing CV optimization (English)...")
    try:
        optimized_cv = optimizer.optimize_cv(
            cv_text=sample_cv,
            job_description=sample_job,
            language="en"
        )
        print("   ✅ CV optimized successfully")
        print(f"   - Name: {optimized_cv.full_name}")
        print(f"   - Email: {optimized_cv.email}")
        print(f"   - Key Skills: {', '.join(optimized_cv.key_skills[:3])}...")
        print(f"   - Experience entries: {len(optimized_cv.experience)}")
    except Exception as e:
        print(f"   ❌ Error optimizing CV: {e}")
        return False
    
    print("\n3. Testing Word document generation...")
    try:
        word_bytes = DocumentGenerator.generate_word(optimized_cv)
        print(f"   ✅ Word document generated ({len(word_bytes)} bytes)")
    except Exception as e:
        print(f"   ❌ Error generating Word document: {e}")
        return False
    
    print("\n4. Testing PDF generation...")
    try:
        pdf_bytes = DocumentGenerator.generate_pdf(optimized_cv)
        print(f"   ✅ PDF generated ({len(pdf_bytes)} bytes)")
    except Exception as e:
        print(f"   ❌ Error generating PDF: {e}")
        return False
    
    print("\n5. Testing Spanish optimization...")
    try:
        sample_cv_es = """
        Juan García
        juan.garcia@email.com
        +34 666 123 456
        Madrid, España
        
        EXPERIENCIA PROFESIONAL
        
        Ingeniero de Software Senior
        Empresa Tecnológica S.L.
        Enero 2020 - Presente
        - Desarrollo de aplicaciones web con Python
        - Liderazgo de equipo de 5 desarrolladores
        - Mejora de rendimiento del sistema en 40%
        
        EDUCACIÓN
        
        Licenciatura en Informática
        Universidad Politécnica
        Graduado: 2018
        """
        
        sample_job_es = """
        Desarrollador Python Senior
        
        Buscamos un Desarrollador Python experimentado.
        
        Requisitos:
        - 5+ años de experiencia con Python
        - Conocimiento de frameworks web (Django, FastAPI)
        - Experiencia con bases de datos SQL
        - Experiencia con AWS
        - Liderazgo de equipos
        """
        
        optimized_cv_es = optimizer.optimize_cv(
            cv_text=sample_cv_es,
            job_description=sample_job_es,
            language="es"
        )
        print("   ✅ Spanish CV optimized successfully")
    except Exception as e:
        print(f"   ❌ Error with Spanish optimization: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! Application is ready to use.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: streamlit run app.py")
    print("2. Open your browser to http://localhost:8501")
    print("3. Paste your CV and job description")
    print("4. Download optimized documents")
    
    return True


if __name__ == "__main__":
    success = test_cv_optimizer()
    exit(0 if success else 1)
