# 📄 AI Resume Analyzer

**🔗 Live demo:** [ai-resume-analyzer-9dnqqh3kkunnzrdjgvj8qy.streamlit.app](https://ai-resume-analyzer-9dnqqh3kkunnzrdjgvj8qy.streamlit.app)

An NLP-powered resume analyzer built with **Python**, **spaCy**, and **Streamlit**,
with optional **LLM API** integration (Groq or OpenAI) for qualitative AI feedback.

Upload a resume (PDF/DOCX/TXT), paste a job description, and instantly get:
- A **match score** between your resume and the job description
- **Matched vs. missing skills** (from a 60+ term tech/AI skills taxonomy)
- **ATS-style resume health checks** (length, contact info, quantified
  impact, action verbs, standard sections)
- Optional **AI-generated qualitative feedback** (strengths, improvements,
  overall verdict) powered by an LLM (Groq's free tier or OpenAI's GPT-4o-mini)

## Why this project is resume-worthy

It demonstrates: file parsing, NLP (tokenization, lemmatization, keyword
extraction with spaCy), building an interactive data app with Streamlit,
designing a scoring algorithm, and integrating a third-party LLM API with
graceful degradation when no API key is available.

## Tech Stack
- **Python 3.12**
- **spaCy** — NLP: keyword & skill extraction
- **Streamlit** — interactive web UI, deployed on Streamlit Community Cloud
- **pdfplumber / python-docx** — resume parsing
- **Groq API / OpenAI API** (optional) — qualitative AI feedback, via an
  OpenAI-compatible client so either provider can be swapped in

## Project Structure
ai-resume-analyzer/
├── app.py # Streamlit entrypoint
├── utils/
│ ├── parser.py # PDF/DOCX/TXT text extraction
│ ├── analyzer.py # skills extraction + scoring (offline NLP)
│ └── ai_feedback.py # optional Groq/OpenAI LLM integration
├── sample_job_description.txt # sample JD to test with
├── runtime.txt # pins Python 3.12 for hosted deployment
├── requirements.txt
└── README.md
## Setup & Run

```bash
# 1. Clone / navigate into the project
cd ai-resume-analyzer

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) enable AI feedback — pick ONE:
# Option A: Groq (free, no credit card — get a key at console.groq.com)
export GROQ_API_KEY="gsk-..."
# Option B: OpenAI (paid, requires billing on platform.openai.com)
export OPENAI_API_KEY="sk-..."
# Windows (PowerShell): $env:GROQ_API_KEY="gsk-..."

# 5. Run the app
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
- Add caching so repeated analyses of the same resume don't re-parse it
