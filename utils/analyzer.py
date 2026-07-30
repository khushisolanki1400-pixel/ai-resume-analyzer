"""
Core NLP analysis engine for the resume analyzer.

Uses spaCy for tokenization / lemmatization and a curated skills
taxonomy to:
  1. Extract skills/keywords found in a resume
  2. Compare them against a job description
  3. Produce a match score and actionable gap analysis

This module works fully offline (no API calls needed) so the app
is useful even without an OpenAI key.
"""
import re
from collections import Counter

import spacy

# The model is installed as a direct pip dependency (see requirements.txt)
nlp = spacy.load("en_core_web_sm")


# A reasonably broad taxonomy of tech/software/AI skills. Extend this list
# freely — it's the main lever for improving extraction quality.
SKILLS_TAXONOMY = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "r", "scala", "kotlin", "swift", "php", "ruby",
    # Web / Full stack
    "react", "angular", "vue", "next.js", "node.js", "express", "django",
    "flask", "fastapi", "spring boot", "html", "css", "tailwind", "redux",
    "graphql", "rest api", "restful api",
    # Data / AI / ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "pytorch", "tensorflow", "keras", "scikit-learn",
    "pandas", "numpy", "hugging face", "transformers", "llm", "openai api",
    "langchain", "rag", "prompt engineering", "generative ai",
    # Data engineering / infra
    "docker", "kubernetes", "aws", "azure", "gcp", "terraform", "ci/cd",
    "git", "github actions", "jenkins", "airflow", "spark", "kafka",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    # Practices
    "agile", "scrum", "microservices", "unit testing", "tdd", "system design",
    "data structures", "algorithms", "object-oriented design",
]

# Sort longest-first so multi-word skills (e.g. "machine learning") are
# matched before their substrings.
SKILLS_TAXONOMY.sort(key=len, reverse=True)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def extract_skills(text: str) -> list[str]:
    """Return the set of taxonomy skills found in the given text."""
    normalized = _normalize(text)
    found = []
    for skill in SKILLS_TAXONOMY:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, normalized):
            found.append(skill)
    return sorted(set(found))


def extract_keywords(text: str, top_n: int = 25) -> list[str]:
    """
    Extract the most frequent meaningful nouns/proper-nouns from text,
    excluding stopwords/punctuation. Useful for surfacing job-description
    keywords that aren't in the fixed skills taxonomy.
    """
    doc = nlp(text)
    candidates = [
        token.lemma_.lower()
        for token in doc
        if token.pos_ in ("NOUN", "PROPN")
        and not token.is_stop
        and token.is_alpha
        and len(token.text) > 2
    ]
    counts = Counter(candidates)
    return [word for word, _ in counts.most_common(top_n)]


def compute_match_score(resume_skills: list[str], jd_skills: list[str]) -> dict:
    """
    Compare resume skills against job-description skills.
    Returns score, matched skills, and missing skills.
    """
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)

    if not jd_set:
        return {"score": None, "matched": [], "missing": [], "extra": sorted(resume_set)}

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    extra = sorted(resume_set - jd_set)

    score = round(100 * len(matched) / len(jd_set), 1)

    return {
        "score": score,
        "matched": matched,
        "missing": missing,
        "extra": extra,
    }


def analyze_resume_structure(text: str) -> dict:
    """
    Lightweight heuristic checks for common ATS/resume best practices.
    Returns a dict of check_name -> (passed: bool, message: str).
    """
    lower = text.lower()
    word_count = len(text.split())

    checks = {}

    checks["length"] = (
        300 <= word_count <= 1200,
        f"Resume has {word_count} words. Aim for roughly 400–900 words "
        "(1 page for <5 yrs experience, up to 2 pages otherwise).",
    )

    has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))
    checks["contact_email"] = (
        has_email, "Email address detected." if has_email else
        "No email address detected — make sure contact info is included."
    )

    has_phone = bool(re.search(r"(\+?\d[\d\-\s()]{7,}\d)", text))
    checks["contact_phone"] = (
        has_phone, "Phone number detected." if has_phone else
        "No phone number detected — consider adding one."
    )

    has_quant = bool(re.search(r"\b\d+%|\$\d+|\b\d{2,}\b", text))
    checks["quantified_impact"] = (
        has_quant,
        "Found quantified achievements (numbers/percentages)." if has_quant else
        "No numbers/metrics detected — quantify impact "
        "(e.g. 'reduced latency by 30%', 'served 10k+ users')."
    )

    action_verbs = [
        "led", "built", "designed", "implemented", "developed", "created",
        "optimized", "launched", "improved", "architected", "automated",
        "reduced", "increased", "managed", "deployed",
    ]
    found_verbs = [v for v in action_verbs if re.search(rf"\b{v}\b", lower)]
    checks["action_verbs"] = (
        len(found_verbs) >= 3,
        f"Found {len(found_verbs)} strong action verbs ({', '.join(found_verbs[:6])})."
        if found_verbs else
        "Few/no strong action verbs found — start bullet points with verbs "
        "like 'Built', 'Led', 'Optimized'.",
    )

    has_sections = any(
        section in lower
        for section in ["experience", "education", "projects", "skills"]
    )
    checks["standard_sections"] = (
        has_sections,
        "Standard resume sections detected." if has_sections else
        "Couldn't detect standard sections (Experience/Education/Skills/Projects) "
        "— use clear section headers so ATS systems can parse your resume."
    )

    return checks
