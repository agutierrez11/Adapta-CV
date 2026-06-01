# 🚀 Guía de Inicio Rápido - CV Optimizer ATS

## Requisitos Previos

- **Python 3.9+** instalado en tu computadora
- **API Key de DeepSeek** (obtén una gratis en https://platform.deepseek.com/api_keys)

## Instalación (5 minutos)

### Paso 1: Descargar el Proyecto

**Opción A - Desde GitHub:**
```bash
git clone <url-del-repositorio>
cd cv_optimizer_ats
```

**Opción B - Descargar ZIP:**
1. Descarga el archivo ZIP del proyecto
2. Extrae la carpeta
3. Abre una terminal en esa carpeta

### Paso 2: Configurar la API Key

#### En Windows:
1. Abre el archivo `.env.example`
2. Copia su contenido
3. Crea un nuevo archivo llamado `.env`
4. Pega el contenido y reemplaza `your_deepseek_api_key_here` con tu clave real
5. Guarda el archivo

#### En macOS/Linux:
```bash
cp .env.example .env
nano .env  # o usa tu editor favorito
# Reemplaza la clave y guarda
```

### Paso 3: Ejecutar la Aplicación

#### En Windows:
```bash
run.bat
```

#### En macOS/Linux:
```bash
./run.sh
```

#### Opción Manual (Cualquier Sistema):
```bash
# Crear entorno virtual (primera vez)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la app
streamlit run app.py
```

## Uso

1. **Abre tu navegador** en `http://localhost:8501`
2. **Pega tu CV** en el panel izquierdo
3. **Pega la descripción del empleo** en el panel derecho
4. **Selecciona el idioma** (Español o English)
5. **Haz clic en "Optimize CV"**
6. **Descarga** tu CV optimizado en Word o PDF

## Solución de Problemas

### "API key not found"
- Verifica que el archivo `.env` exista en la carpeta del proyecto
- Asegúrate de que contiene tu clave de DeepSeek correcta
- Reinicia la aplicación

### "Module not found"
```bash
# Reinstala las dependencias
pip install -r requirements.txt
```

### "Python not found"
- Instala Python desde https://www.python.org/
- Asegúrate de marcar "Add Python to PATH" durante la instalación

### Problemas con PDF en macOS/Linux
```bash
# Instala las dependencias del sistema
# En Ubuntu/Debian:
sudo apt-get install libpango-1.0-0 libpango-1.0-common libpangoft2-1.0-0

# En macOS:
brew install pango
```

## Obtener tu API Key de DeepSeek

1. Ve a https://platform.deepseek.com/api_keys
2. Crea una cuenta (es gratis)
3. Genera una nueva API Key
4. Copia la clave y pégala en tu archivo `.env`

## Costo de Uso

- **Cada CV optimizado cuesta ~$0.002 USD**
- Puedes optimizar **500 CVs por $1 USD**
- Muy económico para uso personal

## Estructura del Proyecto

```
cv_optimizer_ats/
├── app.py                 # Aplicación principal
├── llm_processor.py       # Lógica de IA
├── document_generator.py  # Generación de documentos
├── requirements.txt       # Dependencias
├── .env.example          # Ejemplo de configuración
├── run.sh                # Script de inicio (macOS/Linux)
├── run.bat               # Script de inicio (Windows)
├── README.md             # Documentación completa
└── INICIO_RAPIDO.md      # Esta guía
```

## Consejos para Mejores Resultados

✅ **Haz:**
- Proporciona un CV completo con toda tu experiencia
- Usa descripciones de empleo detalladas
- Revisa el CV optimizado antes de enviar
- Prueba con diferentes empleos

❌ **Evita:**
- CVs muy cortos o incompletos
- Descripciones de empleo vagas
- Cambiar manualmente el CV generado (puede romper el formato ATS)

## Próximos Pasos

1. Optimiza tu primer CV
2. Descarga en Word y PDF
3. Revisa la calidad
4. Envía a las empresas
5. ¡Buena suerte! 🍀

## Soporte

Si encuentras problemas:
1. Verifica la sección "Solución de Problemas" arriba
2. Revisa el archivo `README.md` para más detalles
3. Asegúrate de que tu API Key sea válida

---

**¡Listo para empezar? Ejecuta `run.sh` (macOS/Linux) o `run.bat` (Windows) ahora!**
