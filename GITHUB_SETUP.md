# 📤 Cómo Desplegar en Streamlit Cloud (Gratis)

Como esta aplicación usa Python, no se puede usar GitHub Pages (que es solo para sitios estáticos). La mejor opción gratuita es **Streamlit Community Cloud**.

## Paso 1: Sube el código a tu GitHub

1. Crea un repositorio en GitHub llamado `Adapta-CV`.
2. Sube todos los archivos de la carpeta `cv_optimizer_ats` a ese repositorio.
   - **IMPORTANTE**: No subas el archivo `.env`. Las llaves de API se configuran de forma segura en el panel de Streamlit.

## Paso 2: Desplegar en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io/) e inicia sesión con tu cuenta de GitHub.
2. Haz clic en **"Create app"**.
3. Selecciona tu repositorio: `agutierrez11/Adapta-CV`.
4. Main file path: `app.py`.
5. Haz clic en **"Deploy!"**.

## Paso 3: Configurar tus API Keys (Secrets)

Para que la app funcione sin que tengas que escribir la clave cada vez, puedes guardarlas de forma segura:

1. En el panel de tu app en Streamlit Cloud, ve a **Settings** > **Secrets**.
2. Pega lo siguiente (reemplazando con tus claves reales):

```toml
GROQ_API_KEY = "tu_clave_de_groq_aqui"
DEEPSEEK_API_KEY = "tu_clave_de_deepseek_aqui"
```

3. Haz clic en **Save**. ¡Listo! Tu app ya tendrá acceso a las APIs de forma segura.

## Archivos clave para el despliegue

He incluido estos archivos específicos para que el despliegue en la nube funcione:
- `requirements.txt`: Lista de librerías Python.
- `packages.txt`: Dependencias del sistema (necesarias para generar los PDFs).
- `.streamlit/config.toml`: Configuración visual de la app.

---
¡Tu app estará disponible en una URL como `https://adapta-cv.streamlit.app`!
