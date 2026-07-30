# 📄 AI Resume Analyzer

An NLP-powered resume analyzer built with **Python**, **spaCy**, and **Streamlit**,
with optional **OpenAI API** integration for qualitative AI feedback.

Upload a resume (PDF/DOCX/TXT), paste a job description, and instantly get:
- A **match score** between your resume and the job description
- **Matched vs. missing skills** (from a 60+ term tech/AI skills taxonomy)
- **ATS-style resume health checks** (length, contact info, quantified
  impact, action verbs, standard sections)
- Optional **AI-generated qualitative feedback** (strengths, improvements,
  overall verdict) powered by GPT-4o-mini

## Why this project is resume-worthy

It demonstrates: file parsing, NLP (tokenization, lemmatization, keyword
extraction with spaCy), building an interactive data app with Streamlit,
designing a scoring algorithm, and integrating a third-party LLM API with
graceful degradation when the API key isn't available.

## Tech Stack
- **Python 3.10+**
- **spaCy** — NLP: keyword & skill extraction
- **Streamlit** — interactive web UI
- **pdfplumber / python-docx** — resume parsing
- **OpenAI API** (optional) — qualitative AI feedback

## Project Structure
```
ai-resume-analyzer/
├── app.py                     # Streamlit entrypoint
├── utils/
│   ├── parser.py               # PDF/DOCX/TXT text extraction
│   ├── analyzer.py             # skills extraction + scoring (offline NLP)
│   └── ai_feedback.py          # optional OpenAI API integration
├── sample_job_description.txt  # sample JD to test with
├── requirements.txt
└── README.md
```

## Setup & Run

```bash
# 1. Clone / navigate into the project
cd ai-resume-analyzer

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the spaCy English model
python -m spacy download en_core_web_sm

# 5. (Optional) enable AI feedback by setting your OpenAI API key
export OPENAI_API_KEY="sk-..."     # Windows (PowerShell): $env:OPENAI_API_KEY="sk-..."

# 6. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

> **Note:** The AI-feedback toggle in the sidebar is optional. All core
> features (skill extraction, match scoring, ATS checks) work fully
> offline without any API key.

## Ideas for Extending This Project
- Swap the fixed skills taxonomy for embedding-based semantic matching
  (e.g. sentence-transformers) to catch synonyms like "ML" vs "machine learning"
- Add resume bullet-point rewriting suggestions inline
- Support batch analysis of multiple resumes against one job posting
- Deploy to Streamlit Community Cloud for a live demo link on your resume
