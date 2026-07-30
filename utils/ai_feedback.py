"""
Optional AI-powered qualitative feedback using the OpenAI API.

If no API key is configured, the app still works fully using the
offline NLP analysis in analyzer.py — this module just adds a layer
of natural-language feedback on top when a key is available.
"""
import os

from openai import OpenAI


def get_client() -> OpenAI | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


PROMPT_TEMPLATE = """You are an expert technical recruiter and resume coach.

Given the RESUME TEXT and (optionally) a JOB DESCRIPTION below, provide:
1. Three specific, actionable strengths of this resume.
2. Three specific, actionable improvements (be concrete: rewrite a bullet
   point as an example where possible).
3. A one-paragraph overall verdict on how well this resume would perform
   for the target role.

Keep the tone direct, constructive, and specific to THIS resume — avoid
generic advice.

RESUME TEXT:
---
{resume_text}
---

JOB DESCRIPTION (optional):
---
{job_description}
---
"""


def get_ai_feedback(resume_text: str, job_description: str = "") -> str:
    """
    Calls the OpenAI API to generate qualitative resume feedback.
    Returns an error-friendly message if no API key is set or the call fails.
    """
    client = get_client()
    if client is None:
        return (
            "⚠️ No OpenAI API key configured, so AI-generated qualitative "
            "feedback is unavailable. Set the OPENAI_API_KEY environment "
            "variable to enable this feature. The keyword/skill match "
            "analysis above still works fully offline."
        )

    prompt = PROMPT_TEMPLATE.format(
        resume_text=resume_text[:8000],  # keep prompt within reasonable size
        job_description=job_description[:3000] or "(not provided)",
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert resume coach."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=700,
        )
        return response.choices[0].message.content
    except Exception as exc:  # noqa: BLE001
        return f"⚠️ Could not reach OpenAI API: {exc}"
