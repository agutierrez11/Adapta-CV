# CV Optimizer for ATS 📄

An intelligent resume optimization tool that uses DeepSeek AI to align your CV with job descriptions while maintaining authenticity. Generates ATS-friendly documents in Word and PDF formats.

## Features ✨

- **AI-Powered Optimization**: Uses DeepSeek API to analyze your CV and job description
- **Genuine Matching**: Aligns your real experience with job requirements without exaggeration
- **ATS-Friendly Format**: Single-column layout optimized for Applicant Tracking Systems
- **Bilingual Support**: Works in Spanish and English
- **Multiple Exports**: Generate both Word (.docx) and PDF formats
- **Web Interface**: Easy-to-use Streamlit interface
- **Cost-Effective**: Minimal API costs (fractions of a cent per optimization)

## Prerequisites 📋

- Python 3.9 or higher
- DeepSeek API key (get one at https://platform.deepseek.com/api_keys)
- pip (Python package manager)

## Installation 🚀

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd cv_optimizer_ats
```

Or download the files directly.

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your DeepSeek API Key

**Option A: Using .env file (Recommended)**

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your DeepSeek API key:
```
DEEPSEEK_API_KEY=your_actual_api_key_here
```

**Option B: Using Environment Variable**

```bash
# On Windows (PowerShell):
$env:DEEPSEEK_API_KEY="your_api_key_here"

# On macOS/Linux:
export DEEPSEEK_API_KEY="your_api_key_here"
```

## Usage 🎯

### Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Step-by-Step Guide

1. **Paste Your CV**: Copy your current resume text and paste it in the left panel
2. **Paste Job Description**: Copy the job posting and paste it in the right panel
3. **Select Language**: Choose Spanish (🇪🇸) or English (🇬🇧) from the sidebar
4. **Click "Optimize CV"**: The AI will analyze and optimize your resume
5. **Download**: Get your optimized CV in Word or PDF format

## How It Works 🔧

### The Optimization Process

1. **Analysis**: DeepSeek analyzes your CV and extracts key information
2. **Job Matching**: Identifies keywords and requirements from the job description
3. **Semantic Alignment**: Rewrites your experience to highlight relevant skills
4. **ATS Optimization**: Formats the output for maximum ATS compatibility
5. **Document Generation**: Creates professional Word and PDF files

### Key Principles

- **No Fabrication**: Never invents experience, titles, or skills
- **Genuine Matching**: Aligns real experience with job requirements
- **Terminology Alignment**: Uses exact keywords from the job description
- **Achievement Focus**: Highlights accomplishments using proven formulas
- **ATS Compliance**: Single-column layout, standard fonts, no graphics

## Output Formats 📥

### Word Document (.docx)
- Native Microsoft Word format
- Fully editable
- Best for job portals
- ATS-optimized structure

### PDF
- Professional appearance
- Selectable text (not an image)
- Best for email submissions
- Maintains formatting across devices

## Project Structure 📁

```
cv_optimizer_ats/
├── app.py                    # Main Streamlit application
├── llm_processor.py          # DeepSeek API integration
├── document_generator.py     # Word and PDF generation
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment configuration
├── README.md                # This file
└── .gitignore              # Git ignore file
```

## Troubleshooting 🔧

### "API key not found" Error
- Ensure your `.env` file is in the same directory as `app.py`
- Check that `DEEPSEEK_API_KEY` is correctly set
- Restart the Streamlit app after setting the key

### "Module not found" Error
- Verify all requirements are installed: `pip install -r requirements.txt`
- Make sure you're using the correct virtual environment

### PDF Generation Issues
- WeasyPrint requires system libraries. On Ubuntu/Debian: `sudo apt-get install libpango-1.0-0 libpango-1.0-common libpangoft2-1.0-0`
- On macOS: `brew install pango`
- On Windows: Pre-built binaries are included

### DeepSeek API Errors
- Check your API key is valid at https://platform.deepseek.com/api_keys
- Verify you have API credits available
- Check your internet connection

## Cost Estimation 💰

- **API Cost**: ~$0.002 per CV optimization (using DeepSeek)
- **Hosting (Local)**: $0 USD
- **Hosting (Cloud)**: $0-5 USD/month (optional)

## Tips for Best Results 💡

1. **Provide Complete Information**: Include all relevant experience, skills, and education
2. **Use Clear Formatting**: When pasting your CV, maintain clear section headers
3. **Specific Job Descriptions**: The more detailed the job posting, the better the optimization
4. **Review Before Submitting**: Always review the optimized CV before applying
5. **Test with ATS Tools**: Use free ATS checkers to verify compatibility

## Deployment Options 🌐

### Local Machine
Perfect for personal use. Just run `streamlit run app.py`

### GitHub
1. Initialize git: `git init`
2. Add files: `git add .`
3. Commit: `git commit -m "Initial commit"`
4. Push to GitHub

### Cloud Deployment (Optional)
- **Render**: Free tier available, see https://render.com/
- **Railway**: Pay-as-you-go, see https://railway.app/
- **Fly.io**: Generous free tier, see https://fly.io/

## Privacy & Security 🔒

- Your CV data is only sent to DeepSeek API
- No data is stored on any server (local deployment)
- Your API key should never be committed to version control
- Use `.gitignore` to exclude `.env` file

## API Costs Breakdown 📊

For a typical optimization:
- Input tokens: ~5,000 (your CV + job description)
- Output tokens: ~1,500 (optimized CV)
- Cost with DeepSeek: **~$0.002 USD**

This means you can optimize **500 resumes for $1 USD**

## License 📜

This project is provided as-is for personal use.

## Support & Issues 🆘

If you encounter issues:
1. Check the Troubleshooting section above
2. Review your DeepSeek API configuration
3. Ensure all dependencies are installed
4. Check that your Python version is 3.9+

## Future Enhancements 🚀

Potential improvements:
- ATS score feedback
- Multiple job description comparison
- Cover letter generation
- Interview preparation tips
- Resume templates library

## Changelog 📝

### Version 1.0.0
- Initial release
- DeepSeek API integration
- Word and PDF export
- Bilingual support (Spanish/English)
- Streamlit web interface

---

**Made with ❤️ for job seekers everywhere**

Get your DeepSeek API key: https://platform.deepseek.com/api_keys
