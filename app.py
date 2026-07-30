"""
AI Resume Analyzer
------------------
A Streamlit app that:
  1. Parses an uploaded resume (PDF/DOCX/TXT)
  2. Extracts skills/keywords using NLP (spaCy)
  3. Compares them against a pasted job description
  4. Scores the match and highlights gaps
  5. Optionally generates qualitative feedback via the OpenAI API

Run with:  streamlit run app.py
"""
import streamlit as st

from utils.parser import extract_resume_text
from utils.analyzer import (
    extract_skills,
    extract_keywords,
    compute_match_score,
    analyze_resume_structure,
)
from utils.ai_feedback import get_ai_feedback

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)

st.title("📄 AI Resume Analyzer")
st.caption(
    "Upload your resume, paste a job description, and get an instant "
    "match score, skill-gap analysis, and AI-powered feedback."
)

with st.sidebar:
    st.header("⚙️ Options")
    use_ai_feedback = st.toggle(
        "Enable AI qualitative feedback (uses OpenAI API)", value=False
    )
    st.markdown(
        "AI feedback requires an `OPENAI_API_KEY` environment variable. "
        "Without it, the app still runs fully offline using NLP-based "
        "skill matching."
    )
    st.divider()
    st.markdown(
        "**Tech stack:** Python · spaCy (NLP) · Streamlit · OpenAI API"
    )

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload your resume")
    uploaded_file = st.file_uploader(
        "PDF, DOCX, or TXT", type=["pdf", "docx", "txt"]
    )

with col2:
    st.subheader("2. Paste the job description (optional)")
    job_description = st.text_area(
        "Job description", height=200, placeholder="Paste the job posting here..."
    )

analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=False)

if analyze_clicked:
    if not uploaded_file:
        st.error("Please upload a resume file first.")
        st.stop()

    with st.spinner("Extracting text from resume..."):
        file_bytes = uploaded_file.read()
        try:
            resume_text = extract_resume_text(uploaded_file.name, file_bytes)
        except ValueError as e:
            st.error(str(e))
            st.stop()

    if not resume_text.strip():
        st.error(
            "Couldn't extract any text from this file. If it's a scanned "
            "PDF (image-based), try uploading a text-based version instead."
        )
        st.stop()

    st.success("Resume parsed successfully ✅")

    # ---- Skill extraction ----
    resume_skills = extract_skills(resume_text)

    st.subheader("🧠 Skills Detected in Your Resume")
    if resume_skills:
        st.write(", ".join(f"`{s}`" for s in resume_skills))
    else:
        st.info("No skills from our taxonomy were detected.")

    # ---- Match scoring (only if JD provided) ----
    if job_description.strip():
        jd_skills = extract_skills(job_description)
        result = compute_match_score(resume_skills, jd_skills)

        st.subheader("🎯 Match Score")
        score = result["score"]
        if score is not None:
            st.metric("Resume ↔ Job Description Match", f"{score}%")
            st.progress(min(int(score), 100))

            m1, m2 = st.columns(2)
            with m1:
                st.markdown("**✅ Matched skills**")
                st.write(", ".join(result["matched"]) or "—")
            with m2:
                st.markdown("**❌ Missing skills (consider adding if relevant)**")
                st.write(", ".join(result["missing"]) or "—")
        else:
            st.info("Couldn't detect taxonomy skills in the job description.")

        # Top keywords in JD not necessarily in fixed taxonomy
        with st.expander("📌 Additional job-description keywords (frequency-based)"):
            jd_keywords = extract_keywords(job_description)
            st.write(", ".join(jd_keywords) or "—")
    else:
        st.info(
            "💡 Paste a job description above to get a tailored match score "
            "and skill-gap analysis."
        )

    # ---- Structural / ATS checks ----
    st.subheader("✅ Resume Health Checks")
    checks = analyze_resume_structure(resume_text)
    for name, (passed, message) in checks.items():
        icon = "✅" if passed else "⚠️"
        st.markdown(f"{icon} **{name.replace('_', ' ').title()}** — {message}")

    # ---- Optional AI feedback ----
    if use_ai_feedback:
        st.subheader("🤖 AI-Generated Feedback")
        with st.spinner("Asking the AI coach for feedback..."):
            feedback = get_ai_feedback(resume_text, job_description)
        st.markdown(feedback)

    with st.expander("📄 View extracted resume text"):
        st.text(resume_text)
